#check ckpt, scheduler, model, labels, maps, mloss, accumulate, x['lr'], x['momentum'], imgs, x, npr, g, v

ckpt = torch.load(weights, map_location='cpu')
scheduler = lr_scheduler.LambdaLR(optimizer, lr_lambda=lf)
model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model).to(device)
labels = np.concatenate(dataset.labels, 0)
maps = np.zeros(nc)
mloss = torch.zeros(3, device=device)
accumulate = max(1, np.interp(ni, xi, [1, nbs / batch_size]).round())
x['lr'] = np.interp(ni, xi, [hyp['warmup_bias_lr'] if j == 0 else 0.0, x['initial_lr'] * lf(epoch)])
x['momentum'] = np.interp(ni, xi, [hyp['warmup_momentum'], hyp['momentum']])
imgs = nn.functional.interpolate(imgs, size=ns, mode='bilinear', align_corners=False)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
fi = fitness(np.array(results).reshape(1, -1))
torch.save(ckpt, last)
torch.save(ckpt, best)
torch.save(ckpt, w / f'epoch{epoch}.pt')
x = np.loadtxt(evolve_csv, ndmin=2, delimiter=',', skiprows=1)
x = x[np.argsort(-fitness(x))][:n]
npr = np.random
g = np.array([meta[k][0] for k in hyp.keys()])
v = np.ones(ng)

