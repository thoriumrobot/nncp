#check intermediate_loss

loss = torch.mean(torch.norm(e2_pred - e2, dim=1))

intermediate_loss = loss
