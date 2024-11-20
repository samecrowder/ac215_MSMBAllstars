from sklearn.metrics import accuracy_score, roc_auc_score
import torch


def evaluate_model(model, test_loader):
    model.eval()
    test_preds = []
    test_true = []
    with torch.no_grad():
        for X1, X2, H2H, y in test_loader:
            outputs = model(X1, X2, H2H)
            test_preds.extend(outputs.squeeze().tolist())
            test_true.extend(y.tolist())

    test_auc = roc_auc_score(test_true, test_preds)
    test_acc = accuracy_score(test_true, [1 if p > 0.5 else 0 for p in test_preds])
    return test_auc, test_acc
