import torch

ckpt = torch.load(
    "models/best_segformer_tiles_focaldice.pth",
    map_location="cpu"
)

print(type(ckpt))

if isinstance(ckpt, dict):

    print("\nNumber of keys:", len(ckpt))

    print("\nFirst 20 keys:")

    for i, k in enumerate(ckpt.keys()):

        print(k)

        if i == 19:
            break