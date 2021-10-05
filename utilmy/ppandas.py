# -*- coding: utf-8 -*-
HELP= """


"""
import os, sys, time, datetime,inspect, json, yaml, gc, pandas as pd, numpy as np

def log(*s):
    print(*s, flush=True)

def log2(*s, verbose=1):
    if verbose >0 : print(*s, flush=True)

    
###################################################################################################
###### Pandas #####################################################################################
def pd_random(nrows=100):
   df = pd.DataFrame(np.random.randint(0, 10, size=(nrows, 4)), 
                     columns=list('abcd'))
   return df 


def pd_merge(df1, df2, on=None, colkeep=None):
  ### Faster merge
  cols = list(df2.columns) if colkeep is None else on + colkeep
  return df1.join( df2[ cols   ].set_index(on), on=on, how='left', rsuffix="2")


def pd_plot_multi(df, plot_type=None, cols_axe1:list=[], cols_axe2:list=[],figsize=(8,4), spacing=0.1, **kwargs):
    from pandas import plotting
    from pandas.plotting import _matplotlib
    from matplotlib import pyplot as plt


    plt.figure(figsize= figsize )
    # Get default color style from pandas - can be changed to any other color list
    if cols_axe1 is None: cols_axe1 = df.columns
    if len(cols_axe1) == 0: return
    colors = getattr(getattr(plotting, '_matplotlib').style, '_get_standard_colors')(num_colors=len(cols_axe1 + cols_axe2))
    
    # Displays subplot's pair in case of plot_type defined as `pair`
    if plot_type=='pair':
        ax = df.plot(subplots=True, figsize=figsize, **kwargs)
        plt.show()
        return
    
    # First axis
    ax = df.loc[:, cols_axe1[0]].plot(label=cols_axe1[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=cols_axe1[0])
    ##  lines, labels = ax.get_legend_handles_labels()
    lines, labels = [], []

    i1 = len(cols_axe1)
    for n in range(1, len(cols_axe1)):
        df.loc[:, cols_axe1[n]].plot(ax=ax, label=cols_axe1[n], color=colors[(n) % len(colors)], **kwargs)
        line, label = ax.get_legend_handles_labels()
        lines  += line
        labels += label

    for n in range(0, len(cols_axe2)):
        ######### Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        df.loc[:, cols_axe2[n]].plot(ax=ax_new, label=cols_axe2[n], color=colors[(i1 + n) % len(colors)], **kwargs)
        ax_new.set_ylabel(ylabel=cols_axe2[n])

        ######### Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    ax.legend(lines, labels, loc=0)
    plt.show()
    return ax


def pd_plot_histogram(dfi, path_save=None, nbin=20.0, q5=0.005, q95=0.995, nsample= -1, show=False, clear=True) :
    ### Plot histogram
    from matplotlib import pyplot as plt
    import numpy as np, os, time
    q0 = dfi.quantile(q5)
    q1 = dfi.quantile(q95)

    if nsample < 0 :
        dfi.hist( bins=np.arange( q0, q1,  (  q1 - q0 ) /nbin  ) )
    else :
        dfi.sample(n=nsample, replace=True ).hist( bins=np.arange( q0, q1,  (  q1 - q0 ) /nbin  ) )
    plt.title( path_save.split("/")[-1] )

    if show :
      plt.show()

    if path_save is not None :
      os.makedirs(os.path.dirname(path_save), exist_ok=True)
      plt.savefig( path_save )
      print(path_save )
    if clear :
        # time.sleep(5)
        plt.close()


def pd_filter(df, filter_dict="shop_id=11, l1_genre_id>600, l2_genre_id<80311," , verbose=False) :
    """
     dfi = pd_filter2(dfa, "shop_id=11, l1_genre_id>600, l2_genre_id<80311," )
     dfi2 = pd_filter(dfa, {"shop_id" : 11} )
     ### Dilter dataframe with basic expr
    """
    #### Dict Filter
    if isinstance(filter_dict, dict) :
       for key,val in filter_dict.items() :
          df =   df[  (df[key] == val) ]
       return df

    # pd_filter(df,  ss="shop_id=11, l1_genre_id>600, l2_genre_id<80311," )
    ss = filter_dict.split(",")
    def x_convert(col, x):
      x_type = str( dict(df.dtypes)[col] )
      if "int" in x_type or "float" in x_type :
         return float(x)
      else :
          return x
    for x in ss :
       x = x.strip()
       if verbose : print(x)
       if len(x) < 3 : continue
       if "=" in x :
           coli= x.split("=")
           df = df[ df[coli[0]] == x_convert(coli[0] , coli[1] )   ]

       if ">" in x :
           coli= x.split(">")
           df = df[ df[coli[0]] > x_convert(coli[0] , coli[1] )   ]

       if "<" in x :
           coli= x.split("<")
           df = df[ df[coli[0]] < x_convert(coli[0] , coli[1] )   ]
    return df


def pd_to_file(df, filei,  check=0, verbose=True, show='shape',   **kw):
  import os, gc
  from pathlib import Path
  parent = Path(filei).parent
  os.makedirs(parent, exist_ok=True)
  ext  = os.path.splitext(filei)[1]
  if   ext == ".pkl" :       df.to_pickle(filei,  **kw)
  elif ext == ".parquet" :   df.to_parquet(filei, **kw)
  elif ext in [".csv" ,".txt"] :  df.to_csv(filei, **kw)        
  else :
      log('No Extension, using parquet')
      df.to_parquet(filei + ".parquet", **kw)

  if verbose in [True, 1] :  log(filei)        
  if show == 'shape':        log(df.shape)
  if show in [1, True] :     log(df)
     
  if check in [1, True, "check"] : log('Exist', os.path.isfile(filei))
  #  os_file_check( filei )

  # elif check =="checkfull" :
  #  os_file_check( filei )
  #  dfi = pd_read_file( filei, n_pool=1)   ### Full integrity
  #  log("#######  Reload Check: ",  filei, "\n"  ,  dfi.tail(3).T)
  #  del dfi; gc.collect()
  gc.collect()


def pd_sample_strat(df, col, n):
  ### Stratified sampling
  # n   = min(n, df[col].value_counts().min())
  df_ = df.groupby(col).apply(lambda x: x.sample(n = n, replace=True))
  df_.index = df_.index.droplevel(0)
  return df_


def pd_cartesian(df1, df2) :
  ### Cartesian preoduct
  import pandas as pd
  col1 =  list(df1.columns)
  col2 =  list(df2.columns)
  df1['xxx'] = 1
  df2['xxx'] = 1
  df3 = pd.merge(df1, df2,on='xxx')[ col1 + col2 ]
  try:
        del df3['xxx']
  except:pass

  return df3


def pd_col_bins(df, col, nbins=5):
  ### Shortcuts for easy bin of numerical values
  import pandas as pd, numpy as np
  assert nbins < 256, 'nbins< 255'
  return pd.qcut(df[col], q=nbins,labels= np.arange(0, nbins, 1)).astype('int8')


def pd_dtype_reduce(dfm, int0 ='int32', float0 = 'float32') :
    import numpy as np
    for c in dfm.columns :
        if dfm[c].dtype ==  np.dtype(np.int32) :       dfm[c] = dfm[c].astype( int0 )
        elif   dfm[c].dtype ==  np.dtype(np.int64) :   dfm[c] = dfm[c].astype( int0 )
        elif dfm[c].dtype ==  np.dtype(np.float64) :   dfm[c] = dfm[c].astype( float0 )
    return dfm


def pd_dtype_count_unique(df, col_continuous=[]):
    """Learns the number of categories in each variable and standardizes the data.
        ----------
        data: pd.DataFrame
        continuous_ids: list of ints
            List containing the indices of known continuous variables. Useful for
            discrete data like age, which is better modeled as continuous.
        Returns
        -------
        ncat:  number of categories of each variable. -1 if the variable is  continuous.
    """
    import numpy as np
    def gef_is_continuous(data, dtype):
        """ Returns true if data was sampled from a continuous variables, and false
        """
        if str(dtype) == "object":
            return False

        observed = data[~np.isnan(data)]  # not consider missing values for this.
        rules = [np.min(observed) < 0,
                 np.sum((observed) != np.round(observed)) > 0,
                 len(np.unique(observed)) > min(30, len(observed)/3)]
        if any(rules):
            return True
        else:
            return False

    cols = list(df.columns)
    ncat = {}

    for coli in cols:
        is_cont = gef_is_continuous( df[coli].sample( n=min(3000, len(df)) ).values , dtype = df[coli].dtype )
        if coli in col_continuous or is_cont:
            ncat[coli] =  -1
        else:
            ncat[coli] =  len( df[coli].unique() )
    return ncat


def pd_dtype_to_category(df, col_exclude, treshold=0.5):
  """
    Convert string to category
  """
  import pandas as pd
  if isinstance(df, pd.DataFrame):
    for col in df.select_dtypes(include=['object']):
        if col not in col_exclude :
            num_unique_values = len(df[col].unique())
            num_total_values  = len(df[col])
            if float(num_unique_values) / num_total_values < treshold:
                df[col] = df[col].astype('category')
        else:
            df[col] = pd.to_datetime(df[col])
    return df
  else:
    print("Not dataframe")


def pd_dtype_getcontinuous(df, cols_exclude:list=[], nsample=-1) :
    ### Return continuous variable
    clist = {}
    for ci in df.columns :
        ctype   = df[ci].dtype
        if nsample == -1 :
            nunique = len(df[ci].unique())
        else :
            nunique = len(df.sample(n= nsample, replace=True)[ci].unique())
        if 'float' in  str(ctype) and ci not in cols_exclude and nunique > 5 :
           clist[ci] = 1
        else :
           clist[ci] = nunique
    return clist


def pd_del(df, cols:list):
    ### Delete columns without errors
    for col in cols :
        try:
            del df[col]
        except : pass
    return df


def pd_add_noise(df, level=0.05, cols_exclude:list=[]) :
    import numpy as np, pandas as pd
    df2 = pd.DataFrame()
    colsnum = pd_dtype_getcontinuous(df, cols_exclude)
    for ci in df.columns :
        if ci in colsnum :
           print(f'adding noise {ci}')
           sigma = level * (df[ci].quantile(0.95) - df[ci].quantile(0.05)  )
           df2[ci] = df[ci] + np.random.normal(0.0, sigma, [len(df)])
        else :
           df2[ci] = df[ci]
    return df2


def pd_cols_unique_count(df, cols_exclude:list=[], nsample=-1) :
    ### Return cadinat=lity
    clist = {}
    for ci in df.columns :
        ctype   = df[ci].dtype
        if nsample == -1 :
            nunique = len(df[ci].unique())
        else :
            nunique = len(df.sample(n= nsample, replace=True)[ci].unique())

        if 'float' in  str(ctype) and ci not in cols_exclude and nunique > 5 :
           clist[ci] = 0
        else :
           clist[ci] = nunique

    return clist


def pd_show(df, nrows=100, reader='notepad.exe', **kw):
    """ Show from Dataframe
    """
    import pandas as pd
    from utilmy import os_makedirs
    fpath = 'ztmp/ztmp_dataframe.csv'
    os_makedirs(fpath)
    df.iloc[:nrows,:].to_csv(fpath, sep=",", mode='w')






###########################################################################################################
class dict_to_namespace(object):
    #### Dict to namespace
    def __init__(self, d):
        self.__dict__ = d


def to_dict(**kw):
  ## return dict version of the params
  return kw


def to_timeunix(datex="2018-01-16"):
  if isinstance(datex, str)  :
     return int(time.mktime(datetime.datetime.strptime(datex, "%Y-%m-%d").timetuple()) * 1000)

  if isinstance(datex, datetime)  :
     return int(time.mktime( datex.timetuple()) * 1000)


def to_datetime(x) :
  import pandas as pd
  return pd.to_datetime( str(x) )


def np_list_intersection(l1, l2) :
  return [x for x in l1 if x in l2]


def np_add_remove(set_, to_remove, to_add):
    # a function that removes list of elements and adds an element from a set
    result_temp = set_.copy()
    for element in to_remove:
        result_temp.remove(element)
    result_temp.add(to_add)
    return result_temp


def to_float(x):
    try :
        return float(x)
    except :
        return float("NaN")


def to_int(x):
    try :
        return int(x)
    except :
        return float("NaN")


def is_int(x):
    try :
        int(x)
        return True
    except :
        return False    

def is_float(x):
    try :
        float(x)
        return True
    except :
        return False   




########################################################################################################






###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




