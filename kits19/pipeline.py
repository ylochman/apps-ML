import torch.utils.data

from src.config import config
from src.data import H5CropData
from src.evaluation import Evaluator
from src.train import Trainer
from src.unet import UNet3D
from src.utils import load_checkpoint
import pandas as pd

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--epochs", help="Number of epochs to train", type=int, default=1)
parser.add_argument("--batch", help="Size of train batch", type=int, default=8)
parser.add_argument("--evalbatch", help="Size of eval batch", type=int, default=16)
parser.add_argument("--workers", help="Number of workers", type=int, default=6)
parser.add_argument("--checkpoint", help="Checkpoint name", type=str, default=None)
parser.add_argument("--score", help="Should calculate score", type=bool, default=True)

args = parser.parse_args()
print("Arguments: {}".format(args))
print("Config: {}".format(config))

net = UNet3D(1, 3, False)
if args.checkpoint is not None:
    extra = load_checkpoint(net, args.checkpoint)
else:
    extra = {'epoch': 0}

train_data = H5CropData("train_interpolated_crops.hdf5", "train_interpolated_crops.csv")
train_loader = torch.utils.data.DataLoader(train_data, batch_size=args.batch, num_workers=args.workers, shuffle=True)

trainer = Trainer(net, config, limit=2000)
evaluator = Evaluator(net, config)

for epoch in range(args.epochs):
    trainer.run(train_loader, epochs=1, start_epoch=extra['epoch'] + epoch)
    if epoch > 1:
        evaluator.run(crops_csv_file="val_interpolated_crops.csv", crops_hdf_file="val_interpolated_crops.hdf5",
                      workers=args.workers, batch_size=args.evalbatch, should_score=args.score, eval_file=None)
