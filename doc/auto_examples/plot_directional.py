"""
================
Plot directional
================

"""

import libpysal as lps
import numpy as np

from giddy.directional import Rose

# In[2]:


f = open(lps.examples.get_path('spi_download.csv'), 'r')
lines = f.readlines()
f.close()


# In[3]:


lines = [line.strip().split(",") for line in lines]
names = [line[2] for line in lines[1:-5]]
data = np.array([list(map(int, line[3:])) for line in lines[1:-5]])


# In[4]:


sids  = range(60)
out = ['"United States 3/"',
      '"Alaska 3/"',
      '"District of Columbia"',
      '"Hawaii 3/"',
      '"New England"','"Mideast"',
       '"Great Lakes"',
       '"Plains"',
       '"Southeast"',
       '"Southwest"',
       '"Rocky Mountain"',
       '"Far West 3/"']


# In[5]:


snames = [name for name in names if name not in out]


# In[6]:


sids = [names.index(name) for name in snames]


# In[7]:


states = data[sids,:]
us = data[0]
years = np.arange(1969, 2009)


# In[8]:


us


# In[9]:


rel = states/(us*1.)


# In[10]:


rel[0]


# In[11]:


rel[1]


# In[12]:


rel.shape


# In[13]:


gal = lps.open(lps.examples.get_path('states48.gal'))
w = gal.read()
w.transform = 'r'


# In[14]:


Y = rel[:, [0, -1]]


# In[15]:


Y.shape


# In[16]:


Y


# In[17]:


r4 = Rose(Y, w, k=4)


# ## Visualization

# In[18]:


r4.plot_vectors() # lisa vectors


# In[19]:


r4.plot_origin() # origin standardized


# In[20]:


r4.plot() # Polar


# In[21]:


r4.plot(attribute=Y[:,0]) # condition on starting relative income


# In[22]:


r4.plot(attribute=r4.lag[:,0]) # condition on lag of starting relative income


# ## Inference
# 
# The Rose class contains methods to carry out inference on the circular distribution of the LISA vectors. The first approach is based on a two-sided alternative where the null is that the distribution of the vectors across the segments reflects independence in the movements of the focal unit and its spatial lag. Inference is based on random spatial permutations under the null.

# In[23]:


r4.cuts


# In[24]:


r4.counts


# In[25]:


np.random.seed(1234)


# In[26]:


r4.permute(permutations=999)


# In[27]:


r4.p


# Here all the four sector counts are signficantly different from their expectation under the null.

# A directional test can also be implemented. Here the direction of the departure from the null due to positive co-movement of a focal unit and its spatial lag over the time period results in two  two general cases. For sectors in the positive quadrants (I and III), the observed counts are considered extreme if they are larger than expectation, while for the negative quadrants (II, IV) the observed counts are considered extreme if they are small than the expected counts under the null.

# In[28]:


r4.permute(alternative='positive', permutations=999)
r4.p


# In[29]:


r4.expected_perm


# Finally, a directional alternative reflecting negative association between the movement of the focal unit and its lag has the complimentary interpretation to the positive alternative: lower counts in I and III, and higher counts in II and IV relative to the null.

# In[30]:


r4.permute(alternative='negative', permutations=999)
r4.p
