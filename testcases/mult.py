imgs = nn.functional.interpolate(imgs, size=2*ns, mode='bilinear', align_corners=False)