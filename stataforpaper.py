import pandas as pd
import scipy.stats as stats
import numpy as np
def describe_table(data,col = None, stardict = {0.1:'+',0.05:'*',0.01:'**',0.001:'***'},decimals = 3):
    '''
    :param data:  pandas DataFrame, 数据
    :param col:  list, 输出时变量的顺序，默认为None，即数据的变量默认顺序
    :param stardict:  dict, 显著性的符号
    :param decimals:  int, 输出结果保留小数的位数，默认保留三位小数
    :return:  返回三个DataFrame的list
    '''
    if col == None:
        col = data.columns.tolist()
    data = data[col]

    # 描述性统计
    describe_full = data.describe().T.reset_index().rename(columns = {'index':'var'})
    describe_full = describe_full.round(decimals=decimals)  # 四舍五入保留小数位数
    describe_sdmean = describe_full[['var','mean','std']].rename(columns = {'mean':'Mean','std':'S.D.'}).round(decimals=decimals)

    # 计算Pearson相关系数
    corr = data.corr()
    corr_nosig = corr.copy()
    corr_nosig = corr_nosig.reset_index().rename(columns={'index': 'var'}).round(decimals=decimals)

    corr.columns = ['{}_corr'.format(i) for i in corr.columns]
    corr = corr.reset_index().rename(columns = {'index':'var'})
    corr = corr.round(decimals=decimals)  # 四舍五入保留小数位数

    # 计算相关系数的显著性
    for v in corr['var'].values:
        corr['{}_sig'.format(v)] = corr['var'].apply(lambda x: judge_star(stats.pearsonr(data[v],data[x])[1], stardict = stardict))
        corr[v] = corr.apply(lambda x: '{:.3f}{}'.format(x['{}_corr'.format(v)],x['{}_sig'.format(v)]),axis = 1)
    corr = corr[['var']+corr['var'].values.tolist()]

    # 整理相关系数矩阵
    col = corr['var'].values.tolist()
    for v in corr['var'].values:
        corr[v] = corr.apply(lambda x: np.nan if col.index(v) > col.index(x['var']) else x[v], axis =1)
        corr_nosig[v] = corr_nosig.apply(lambda x: np.nan if col.index(v) > col.index(x['var']) else x[v], axis=1)

    # 修正一下列名
    col_index_dict = {c:str(col.index(c)+1) for c in col}
    col_index_dict.update({'var':'var'})
    corr.columns = [col_index_dict[i] for i in corr.columns]

    corr_nosig.columns = [col_index_dict[i] for i in corr_nosig.columns]

    # 合并表格
    des_tab = describe_sdmean.merge(corr, on = 'var')
    des_tab_nosig = describe_sdmean.merge(corr_nosig, on = 'var')
    des_tab_full = describe_full.merge(corr,on = 'var')

    # 修正var列名称
    des_tab['var'] = des_tab['var'].apply(lambda x: '{}. {}'.format(col_index_dict[x], x))
    des_tab_nosig['var'] = des_tab_nosig['var'].apply(lambda x: '{}. {}'.format(col_index_dict[x], x))
    des_tab_full['var'] = des_tab_full['var'].apply(lambda x: '{}. {}'.format(col_index_dict[x], x))
    return [des_tab,des_tab_nosig, des_tab_full]


def judge_star(sig,stardict = {0.1:'+',0.05:'*',0.01:'**',0.001:'***'}):
    '''

    :param sig:  float, p-value
    :param stardict:  dict
    :return:
    '''
    judge_range = list(stardict.keys())
    judge_range.sort()
    temp = judge_range.copy()
    temp.append(sig)
    temp.sort()
    sig_i = temp.index(sig)
    if sig_i > len(judge_range)-1:
        star = ' '
    else:
        star = stardict[judge_range[temp.index(sig)]]
    return star


if __name__ == '__main__':
    data = pd.read_csv('test.csv')
    col = None
    r = describe_table(data = data,col = col)
    with pd.ExcelWriter('result.xlsx') as writer:
        r[0].to_excel(writer,sheet_name= 'description_table', index= False)
        r[1].to_excel(writer,sheet_name= 'description_table_nosig', index= False)
        r[2].to_excel(writer, sheet_name='description_table_full', index=False)

