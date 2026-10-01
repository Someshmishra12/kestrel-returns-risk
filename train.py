"""Reproduce model + predictions. Put train.csv, test_unlabelled.csv in ./data (not shipped: client data, policy s10)."""
import pandas as pd, numpy as np, joblib
from feats import load, build
from sklearn.ensemble import HistGradientBoostingClassifier as H
cust=pd.read_csv('customers.csv'); prod=pd.read_csv('products.csv')
tr=load('data/train.csv',True); te=load('data/test_unlabelled.csv',False)   # dedupes partner_feed rows
X,m=build(tr,cust,prod); y=tr.returned.values; Xt,_=build(te,cust,prod)
cols=[c for c in X if c not in ['sku','note_kind','state','pin3']]; cats=[c for c in cols if str(X[c].dtype)=='category']
for c in cats:
    u=sorted(set(X[c].astype(str))|set(Xt[c].astype(str))); X[c]=pd.Categorical(X[c].astype(str),categories=u); Xt[c]=pd.Categorical(Xt[c].astype(str),categories=u)
mod=H(categorical_features=cats,learning_rate=0.05,max_iter=200,max_depth=3,min_samples_leaf=40,l2_regularization=1.0,random_state=0).fit(X[cols],y)
pd.DataFrame({'order_id':te.order_id,'score':np.round(mod.predict_proba(Xt[cols])[:,1],5)}).to_csv('predictions.csv',index=False)
joblib.dump(dict(model=mod,cols=cols,cats=cats,cat_levels={c:list(X[c].cat.categories) for c in cats},med={c:float(X[c].median()) for c in cols if c not in cats},base=float(y.mean())),'model.joblib')
