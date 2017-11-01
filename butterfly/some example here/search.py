# -*- coding: utf-8 -*-
'''
get a list from OpenFOAM file that indexed with something like 'leftWall.value'or 'leftWall.base.value'
can only read values that in '(' and ')'
'''
import numpy as np
def search_in_dict(file,dirname):
    try:#如果有子类
        dot_index=dirname.index('.')
        father_index = file.index(dirname[:dot_index]) + len(dirname[:dot_index])
        fil=file[father_index:]
        return search_in_dict(fil, dirname[dot_index + 1:])
    except ValueError:#如果没有子类
        tem=file[file.index(dirname)+len(dirname):]#只要类名后的那块,方便找下一个}
        bracket_index = tem.index('(')
        inv_bracket_index=tem.index(')')
        string=file[file.index(dirname)+len(dirname)+bracket_index+1:file.index(dirname)+len(dirname)+inv_bracket_index]
        return np.fromstring(string, dtype=float, sep=' ')

def get_v(filedir,dataname):
    with open(filedir, 'r') as f:
        d=f.read()
    return search_in_dict(d,dataname)