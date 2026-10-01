import pandas as pd, numpy as np, re
LEAK=['last_service_event_type','pickup_scheduled_at']  # post-dispatch / post-return fields: never used
def load(path, labelled):
    d=pd.read_csv(path,parse_dates=['order_placed_at'])
    if labelled:
        d['_s']=(d.source!='crm').astype(int)
        d=d.sort_values(['order_id','_s']).drop_duplicates('order_id',keep='first').drop(columns='_s')
    return d.reset_index(drop=True)
def build(d, cust, prod):
    m=d.merge(cust,on='customer_id',how='left').merge(prod,on='sku',how='left')
    exp=m.list_price_inr*m.qty*(1-m.discount_pct/100)
    m['order_value_fixed']=np.where(m.order_value_inr/exp>50, m.order_value_inr/100, m.order_value_inr)
    f=pd.DataFrame(index=m.index)
    f['discount_pct']=m.discount_pct; f['qty']=m.qty
    f['order_value']=m.order_value_fixed; f['list_price']=m.list_price_inr
    f['promised_days']=m.promised_delivery_days
    f['no_address']=(m.delivery_pincode==0).astype(int)
    f['pin3']=np.where(m.delivery_pincode==0,-1,m.delivery_pincode//1000)
    f['is_gift']=(m.is_gift=='Y').astype(int)
    f['prior_orders']=m.customer_prior_orders; f['prior_returns']=m.customer_prior_returns
    f['prior_ret_rate']=m.customer_prior_returns/m.customer_prior_orders.replace(0,np.nan)
    f['shield']=(m.shield_member=='Y').astype(int)
    f['tenure_days']=(m.order_placed_at-pd.to_datetime(m.signup_date)).dt.days
    f['warranty_months']=m.warranty_months
    f['product_age_days']=(m.order_placed_at-pd.to_datetime(m.launch_date)).dt.days
    f['hour']=m.order_placed_at.dt.hour; f['dow']=m.order_placed_at.dt.dayofweek
    note=m.delivery_note.fillna('').str.replace(r'\d+','#',regex=True).str.slice(0,28)
    f['has_note']=(m.delivery_note.notna()).astype(int)
    for c,col in [('sales_channel','sales_channel'),('payment_mode','payment_mode'),('family','family'),('state','state'),('sku','sku')]:
        f[c]=m[col].astype('category')
    f['note_kind']=note.astype('category')
    return f,m
