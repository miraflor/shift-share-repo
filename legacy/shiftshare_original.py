import os, glob, string, csv, math, numpy as np
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

for input_file in glob.glob(os.path.join(path+"\input",'*.csv')):
    print("Processing: "+input_file)

    input = open(input_file, "r", errors='ignore')
    reader = csv.reader(input)
    
    # Initialize output file
    name, ext = os.path.splitext(input_file)
    name = name.replace("input","output")+"_SS"
    output_file = name+ext
    output = open(output_file, 'w', newline='', errors='ignore')
    writer = csv.writer(output)
    output.close()
    
    # Get data first from file
    industry = list()
    region = list()
    time = list()
    table = list()
    tag = list()
    i = j = row_num = 0
    for row in reader:
        data = row[2:len(row)]
        if row_num==0:
            time = data
        else:
            # Check if industry is new
            if(row[0] not in industry):
                industry.append(row[0])
                i_ = len(industry)-1
            else: # Search for industry
                for i in range(0,len(industry)):
                    if industry[i] == row[0]:
                        i_ = i
                        break
            # Check if region is new
            if(row[1] not in region):
                region.append(row[1])
                j_ = len(region)-1
            else: # Search for region
                for j in range(0,len(region)):
                    if region[j] == row[1]:
                        j_ = j
                        break
            tag.append([i_,j_])
            table.append(data)
        row_num += 1
    
    # Sizes of variables
    I = len(industry) # number of industries
    R = len(region) # number of regions
    T = len(time) # number of time periods
    
    # Fill the variable matrix
    e = np.zeros((I,R,T))
    n = 0
    while n<len(tag):
        m = 0
        while m<len(table[n]):
            val = 0
            if(table[n][m]!=''):
                val = float(table[n][m])
            e[tag[n][0],tag[n][1],m] = val
            m += 1
        n += 1
    
    # e.shape = (I,R,T)
    
    # Tracking changes
    delta = np.zeros((I,R,T))
    delta[:,:,1:T] = e[:,:,1:T]-e[:,:,0:T-1]
    
    # Dimensional Slices
    reg = e.sum(0) # Time series of reg. values (after summing across ind.)
    ind = e.sum(1) # Time series of ind. values (after summing across reg.)
    nat = reg.sum(0) # or ind.sum(0) - Time series of national values

    # Laplace smoothing, also to prevent division by zero
    laplace = 0.0000000000000000000000000000000000000000000001 

    # Growth Rate in Regions across time
    reg_g = np.zeros((R,T))
    curr = reg[:,1:T]
    past = reg[:,0:T-1] + laplace
    reg_g[:,1:T] = (curr-past)/past
    
    # Growth Rate in Industries across time
    ind_g = np.zeros((I,T))
    curr = ind[:,1:T]
    past = ind[:,0:T-1] + laplace
    ind_g[:,1:T] = (curr-past)/past
    
    # Growth Rate in the Nation across time
    nat_g = np.zeros((T))
    curr = nat[1:T]
    past = nat[0:T-1] + laplace
    nat_g[1:T] = (curr-past)/past

    # Projecting Growth Rates in (I,R,T) matrices
    reg_gf = np.zeros((I,R,T))
    ind_gf = np.zeros((I,R,T))
    nat_gf = np.zeros((I,R,T))
    for i in range(0,I):
        for j in range(0,R):
            for t in range(0,T):
                reg_gf[i,j,t] = reg_g[j,t]    
                ind_gf[i,j,t] = ind_g[i,t]
                nat_gf[i,j,t] = nat_g[t]
    
    # Growth Rate in each Industry-Sector Pair across time    
    _g = np.zeros((I,R,T))
    curr = e[:,:,1:T]
    past = e[:,:,0:T-1] + laplace
    _g[:,:,1:T] = (curr-past)/past
    
    
    # Homothetic value and location quotient in industry i of region j at time t
    h = np.zeros((I,R,T)) # Homothetic value
    LQ = np.ones((I,R,T)) # Location quotient
    for i in range(0,I):
        for j in range(0,R):
            for t in range(0,T):
                h[i,j,t] = reg[j,t]*ind[i,t]/(nat[t]+laplace)
                LQ[i,j,t] = e[i,j,t]/h[i,j,t]

    '''
    Computing for Shift Share Elements
    '''
    
    # Declaring Variables
    ENG = np.zeros((I,R,T)) # Expected National Growth Effect
    DNG = np.zeros((I,R,T)) # Differential National Growth Effect
    ENI = np.zeros((I,R,T)) # Expected National Industry Mix Effect
    DNI = np.zeros((I,R,T)) # Differential National Industry Mix Effect
    ERG = np.zeros((I,R,T)) # Expected Regional Growth Effect
    DRG = np.zeros((I,R,T)) # Differential Regional Growth Effect
    ERI = np.zeros((I,R,T)) # Expected Regional Industry Mix Effect
    DRI = np.zeros((I,R,T)) # Differential Regional Industry Mix Effect
    x1 = ind_gf-nat_gf
    x2 = reg_gf-nat_gf
    x3 = _g-reg_gf
    x4 = x3-x1

    '''
    for t in range(1,T):
        ENG[:,:,t] = h[:,:,t-1]*nat_gf[:,:,t]
        DNG[:,:,t] = (e[:,:,t-1]-h[:,:,t-1])*nat_gf[:,:,t]
        ENI[:,:,t] = h[:,:,t-1]*x1[:,:,t]
        DNI[:,:,t] = (e[:,:,t-1]-h[:,:,t-1])*x1[:,:,t]
        ERG[:,:,t] = h[:,:,t-1]*x2[:,:,t]
        DRG[:,:,t] = (e[:,:,t-1]-h[:,:,t-1])*x2[:,:,t]
        ERI[:,:,t] = h[:,:,t-1]*x4[:,:,t]
        DRI[:,:,t] = (e[:,:,t-1]-h[:,:,t-1])*x4[:,:,t]
    
    # Verify that delta = ENG + DNG + ENI + DNI + ERG + DRG + ERI + DRI
    residual = delta - (ENG + DNG + ENI + DNI + ERG + DRG + ERI + DRI)        
    #print(residual)
    '''

    # Period
    period = 5

    #'''
    p = 0
    for t in range(1,T):
        if (p<period):
            p += 1
        for k in range(t-p,t):
            ENG[:,:,t] += h[:,:,k-1]*nat_gf[:,:,k]
            DNG[:,:,t] += (e[:,:,k-1]-h[:,:,k-1])*nat_gf[:,:,k]
            ENI[:,:,t] += h[:,:,k-1]*x1[:,:,k]
            DNI[:,:,t] += (e[:,:,k-1]-h[:,:,k-1])*x1[:,:,k]
            ERG[:,:,t] += h[:,:,k-1]*x2[:,:,k]
            DRG[:,:,t] += (e[:,:,k-1]-h[:,:,k-1])*x2[:,:,k]
            ERI[:,:,t] += h[:,:,k-1]*x4[:,:,k]
            DRI[:,:,t] += (e[:,:,k-1]-h[:,:,k-1])*x4[:,:,k]
    #'''
    
    #'''
    sscomponents = {
        'Expected National Growth Effect': ENG, 
        'Differential National Growth Effect' : DNG,
        'Expected National Industry Mix Effect' : ENI, 
        'Differential National Industry Mix Effect' : DNI, 
        'Expected Regional Growth Effect' : ERG, 
        'Differential Regional Growth Effect' : DRG, 
        'Expected Regional Industry Mix Effect' : ERI, 
        'Differential Regional Industry Mix Effect' : DRI         
    }
    #'''
    
    '''
    sscomponents = {
        'ENG': ENG, 
        'DNG' : DNG,
        'ENI' : ENI, 
        'DNI' : DNI, 
        'ERG' : ERG, 
        'DRG' : DRG, 
        'ERI' : ERI, 
        'DRI' : DRI         
    }
    '''
    
    rows = [['Shift-Share Component','Industry','Region','Year','Value']]
        
    # Save report
    for key, value in sscomponents.items():
        for i in range(0,I):
            for j in range(0,R):
                for t in range(0,T):
                    rows.append([key,industry[i],region[j],time[t],value[i,j,t]])

    output = open(output_file, 'a', newline='')
    writer = csv.writer(output)
    writer.writerows(rows)
    output.close()    