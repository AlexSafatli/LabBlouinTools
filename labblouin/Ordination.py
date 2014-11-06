#!/bin/python

''' 
Ordination is a class designed to compute and plot ordination methods such as PCA and MDS.
It is intended as a helper function to PDBnet, but have the functionality to work with 
gm files.

This file is based on Nelle Varoquaux <nelle.varoquaux@gmail.com> code plotmds.py, available
at http://scikit-learn.org/stable/auto_examples/manifold/plot_mds.html, and recomendations in
stackoverflow by Jaime Fernandez (http://numericalrecipes.wordpress.com/)

Dependencies: SKlearn, PDBnet

Author: Jose Sergio Hleap
email: jshleap@dal.ca
'''

# importing bit###################################################################################
import numpy as np
import scipy.spatial.distance as sp
from sklearn import manifold
from sklearn.metrics import euclidean_distances
from sklearn.decomposition import PCA
from sklearn.lda import LDA
from sklearn.qda import QDA
from utils.PDBnet import PDBstructure as P
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
from random import shuffle
# END importing bit###############################################################################

# Constants ######################################################################################
colors=['b','r','k','g','y','m','c']
hexa  =[
    '#ED9121', '#EE8262', '#EE1289', '#556B2F', '#FF8C00', '#8B7B8B', '#0000EE', '#EED5D2', 
    '#BA55D3', '#912CEE', '#2F4F4F', '#D15FEE', '#008B8B', '#B23AEE', '#8B7765', '#54FF9F',
    '#8B8386', '#FF4040', '#EEA9B8', '#388E8E', '#6E8B3D', '#33A1C9', '#EE3A8C', '#FF00FF',
    '#436EEE', '#8B864E', '#808000', '#1874CD', '#BCD2EE', '#A9A9A9', '#F4A460', '#FF3030',
    '#FFEBCD', '#B0C4DE', '#00CDCD', '#C0FF3E', '#FFD700', '#8B4513', '#4EEE94', '#CD3278',
    '#00E5EE', '#E3A869', '#CD853F', '#ADD8E6', '#CD2990', '#EEE5DE', '#66CD00', '#7B68EE',
    '#FFA54F', '#A2B5CD', '#BC8F8F', '#8B2323', '#EE30A7', '#EEEED1', '#AEEEEE', '#5E2612',
    '#FF7F00', '#FFC0CB', '#EE3B3B', '#9370DB', '#848484', '#292421', '#CDBA96', '#B4EEB4',
    '#40E0D0', '#8B795E', '#3D9140', '#CDB7B5', '#CAE1FF', '#F0FFFF', '#2E8B57', '#FF6103',
    '#87CEEB', '#CD00CD', '#CDAA7D', '#836FFF', '#EEB4B4', '#8B7355', '#F0E68C', '#CDCDB4',
    '#B4CDCD', '#F0FFF0', '#00EEEE', '#708090', '#9AFF9A', '#FFA07A', '#FFB5C5', '#00688B',
    '#8A3324', '#191970', '#308014', '#FF83FA', '#838B8B', '#808A87', '#00FF7F', '#FFA500',
    '#EEAD0E', '#CD3333', '#4876FF', '#7CCD7C', '#EE5C42', '#AAAAAA', '#DAA520', '#8B3A3A',
    '#FFFAF0', '#B2DFEE', '#00EE76', '#FFFAFA', '#800080', '#C5C1AA', '#EEE685', '#FF3E96',
    '#EE0000', '#FDF5E6', '#EECFA1', '#8DB6CD', '#FF7256', '#7CFC00', '#838B83', '#BF3EFF',
    '#8B6914', '#00CD66', '#A4D3EE', '#00868B', '#8DEEEE', '#8B1C62', '#CDBE70', '#9F79EE', 
    '#C1CDC1', '#CD69C9', '#E0EEEE', '#8B7E66', '#8A2BE2', '#CDCD00', '#97FFFF', '#EEAEEE', 
    '#DC143C', '#CD919E', '#528B8B', '#CD6889', '#E6E6FA', '#E3CF57', '#4B0082', '#FF9912',
    '#F0F8FF', '#FF7F50', '#6CA6CD', '#8B8B83', '#F4F4F4', '#548B54', '#48D1CC', '#C1CDCD', 
    '#E0EEE0', '#3D59AB', '#FFB90F', '#FFD39B', '#8B5A2B', '#9C661F', '#EEE9BF', '#BCEE68',
    '#8EE5EE', '#8B0A50', '#FFF68F', '#EEA2AD', '#CD5B45', '#7FFF00', '#8B8378', '#9BCD9B',
    '#EEE8AA', '#8E8E38', '#668B8B', '#B3EE3A', '#00C78C', '#FFC125', '#8B475D', '#D8BFD8',
    '#FFE4C4', '#96CDCD', '#CDB5CD', '#00C5CD', '#00CED1', '#008B00', '#B8860B', '#1C86EE',
    '#EEC591', '#E066FF', '#B7B7B7', '#DEB887', '#FF6EB4', '#6959CD', '#90EE90', '#8B4789',
    '#EE7AE9', '#8968CD', '#D2B48C', '#FFFFE0', '#CDC9C9', '#BDB76B', '#00C957', '#EEDC82',
    '#3CB371', '#F5FFFA', '#B9D3EE', '#F5F5DC', '#0000CD', '#FF8247', '#EED5B7', '#FFEC8B',
    '#EE7600', '#7171C6', '#8B636C', '#8B814C', '#FFE4B5', '#1E1E1E', '#4F94CD', '#CDAD00', 
    '#CD5555', '#71C671', '#8B7500', '#473C8B', '#B0E0E6', '#FFFF00', '#8B4C39', '#006400',
    '#53868B', '#8B2252', '#FFB6C1', '#63B8FF', '#FFAEB9', '#EE6A50', '#87CEFF', '#87CEFA',
    '#5B5B5B', '#ADFF2F', '#008B45', '#EE4000', '#8A360F', '#8B6969', '#00008B', '#DB7093',
    '#7EC0EE', '#EE799F', '#CD6090', '#C76114', '#8B8682', '#458B74', '#FFF5EE', '#76EE00',
    '#000080', '#228B22', '#8B8B00', '#CD950C', '#EE82EE', '#282828', '#F5DEB3', '#3A5FCD',
    '#00FA9A', '#C67171', '#D1EEEE', '#8B5742', '#8B3E2F', '#CD3700', '#9AC0CD', '#555555',
    '#8B8989', '#EED8AE', '#551A8B', '#778899', '#FFFACD', '#458B00', '#008000', '#FFFFF0',
    '#EEB422', '#5CACEE', '#CD4F39', '#CDC0B0', '#FF7D40', '#8E388E', '#6E7B8B', '#CDC673',
    '#7A378B', '#E0FFFF', '#FFFFFF', '#6C7B8B', '#FFC1C1', '#8B4726', '#515151', '#CD9B1D',
    '#FF6347', '#FF34B3', '#FF0000', '#B0E2FF', '#8B3A62', '#CD5C5C', '#A2CD5A', '#00EE00',
    '#FF6A6A', '#CD6600', '#FFEFDB', '#E9967A', '#EEE9E9', '#7A67EE', '#CD8162', '#00F5FF',
    '#FFEFD5', '#CDAF95', '#00BFFF', '#CDB79E', '#1E90FF', '#EE2C2C', '#8B6508', '#FF7F24',
    '#8FBC8F', '#66CDAA', '#6495ED', '#EEE0E5', '#C1C1C1', '#B22222', '#EE00EE', '#FF82AB',
    '#AB82FF', '#79CDCD', '#7D26CD', '#03A89E', '#8B008B', '#5D478B', '#8B3626', '#808069',
    '#FFE4E1', '#EEDFCC', '#9400D3', '#BFEFFF', '#8B7D6B', '#FF8C69', '#C6E2FF', '#FF4500',
    '#FFE7BA', '#872657', '#808080', '#EE9572', '#CD8500', '#8B5A00', '#9932CC', '#EECBAD',
    '#CD8C95', '#CD1076', '#7D9EC0', '#104E8B', '#8B668B', '#698B22', '#EEE8CD', '#DDA0DD',
    '#4169E1', '#DA70D6', '#DCDCDC', '#68228B', '#CDC8B1', '#000000', '#6B8E23', '#FF69B4',
    '#800000', '#5F9EA0', '#8B4500', '#FCE6C9', '#D3D3D3', '#CDB38B', '#607B8B', '#F08080',
    '#CD9B9B', '#76EEC6', '#FAEBD7', '#68838B', '#EAEAEA', '#7FFFD4', '#C0C0C0', '#EE9A49',
    '#4A708B', '#008080', '#7AC5CD', '#98F5FF', '#8B2500', '#FFF0F5', '#8B8970', '#8B8878',
    '#6A5ACD', '#4682B4', '#EEEEE0', '#27408B', '#00FF00', '#FFDEAD', '#CD2626', '#CD96CD',
    '#9B30FF', '#36648B', '#F8F8FF', '#EEC900', '#EEEE00', '#FFE1FF', '#C1FFC1', '#CDC5BF',
    '#A0522D', '#8B5F65', '#CDC1C5', '#EE7621', '#FFBBFF', '#CD6839', '#698B69', '#BDFCC9',
    '#CD661D', '#FAFAD2', '#CDCDC1', '#FFF8DC', '#B452CD', '#8E8E8E', '#8470FF', '#483D8B',
    '#BBFFFF', '#0000FF', '#EE6AA7', '#EE7942', '#00CD00', '#9ACD32', '#C71585', '#EE9A00',
    '#CAFF70', '#32CD32', '#8B0000', '#B0171F', '#98FB98', '#8B1A1A', '#00B2EE', '#20B2AA',
    '#009ACD', '#A52A2A', '#EE6363', '#FAF0E6', '#8B7D7B', '#9A32CD', '#FF8000', '#7A8B8B',
    '#CD7054', '#9FB6CD', '#CDC9A5', '#D02090', '#00FFFF', '#CD0000', '#43CD80', '#FA8072',
    '#FFDAB9', '#D2691E']
shuffle(hexa)
colors.extend(hexa)
# END Constants ##################################################################################

# Functions bit###################################################################################
class ORD:
	'''
	A class for the most popular ordination methods using PDBnet instaces or gm files.
	'''
	def __init__(self,prefix,data,fastafile=None,n_comp=2):
		self.prefix = prefix
		self.fasta  = fastafile
		self.ncomp  = n_comp

		# vessel for ellipses if created
		self.ellipses={}

		#check if data is PDBnet instance or a filename
		if isinstance(data, P): self.PrepData4PDBnet(data)
		elif isinstance(data,str): self.LoadDataGMfile(data)

		# Center the data
		self.data -= self.data.mean(axis=0)


	def PrepData4PDBnet(self,data):
		'''Load the data to the class assuming is a PDBnet instance file'''
		if data.GetModelNames(): ismodel = True
		else: ismodel = False
		self.labels,self.data = data.gm(self.fasta,ismodel=ismodel,typeof='matrix')


	def LoadDataGMfile(self,data):
		'''Load the data to the class assuming is a GM file'''
		coords , labels = [],[]
		with open(data) as F:
			for line in F:
				bl=line.strip().strip(';').split(';')
				labels.append(bl[0].strip('>'))
				coords.append([float(x) for x in bl[1:]])
		self.data   = np.matrix(coords)
		self.labels = labels
	
	def dict2array2matrix(self,dict):
		'''
		Giving an upper-triangle distance matrix in a dictionary, returns a distance-like array
		'''
		ar=[]
		keys = sorted(dict.keys())
		for k in sorted(keys):
			for ke in sorted(keys):
				if ke > k:
					ar.append[dict[k][ke]]
		dist = sp.squareform(np.array(ar))
		return dist
	
	def MDS(self,typeof='classic',dist=False,groups=None,MD=False, dpi=100,textsize=10):
		'''
		Perform Multidimensional Scaling wither classic (PCoA) or non-metric.
		If you have the upper triangle of a distance matrix as a dictionary,
		pass the dictionary as dist.
		'''
		# Rotation instance
		self.clf = PCA(n_components=self.ncomp)		

		seed = np.random.RandomState(seed=3)

		if typeof == 'classic': 
			metric = True
			self.type = 'cMDS'
		else: 
			metric = False
			self.type = "nMDS"
		
		if dist:
			similarities=self.dict2array2matrix(dist)
		else:
			similarities = euclidean_distances(self.data)

		# Initiate multidimensional scaling
		mds = manifold.MDS(n_components=self.ncomp, metric = metric, max_iter=3000, eps=1e-9, 
		                   random_state=seed, dissimilarity="precomputed", n_jobs=-1)

		#fit the data the MDS
		pos = mds.fit(similarities).embedding_
		if typeof != 'classic': pos = mds.fit_transform(similarities, init=pos)

		# Rescale the data
		pos *= np.sqrt((np.array(self.data)** 2).sum()) / np.sqrt((pos ** 2).sum())

		# Rotate the data
		self.fit = self.clf.fit_transform(pos)
		self.Plot(groups=groups, MD=MD,dpi=dpi, fontsize=textsize)


	def PCA(self,groups=None,MD=False,dpi=100,textsize=10):
		'''Performs a principal coordinate analysis of the data'''
		# Rotation instance
		self.clf = PCA(n_components=self.ncomp)		
		pca = self.clf.fit_transform(self.data)
		self.type='PCA'
		self.fit = pca
		self.explained_variance_ratio = pca.explained_variance_ratio_
		self.Plot(groups=groups, dpi=dpi, fontsize=textsize,MD=MD)


	def Plot(self,groups=None,dpi=100,fontsize=10,MD=False):
		'''
		Plot the components from an ordination method of the class ORD. If the number of components
		is greater than 3, it will plot the first three components. Components has to be a n x k 
		numpy array of eigenvectors, where n is the observations/individuals and k the components.
		The option groups allow to pass a list (of the same lenght of the arrar, that is a lenght of n).
		'''
		components=self.fit
		markers = ['k.','b+','g*','r.','c+','m*','y.','k+','b*','g.','r+','c*','m.','y+','k*','b.',
		           'g+','r*','c.','m+','y*']	

		if components.shape[1] >= 3: 
			dim = 3
			fig = plt.figure(dpi=dpi)
			ax  = fig3D.gca(projection='3d')

		else: 
			dim = 2
			fig = plt.figure(dpi=dpi)
			ax  = fig.add_subplot(111)

		comp = components[:, 0:dim]

		ax.spines['top'].set_color('none')
		ax.xaxis.tick_bottom()
		ax.spines['right'].set_color('none')
		ax.yaxis.tick_left()

		if groups and len(groups) <= len(markers):
			d = {}
			g=set(groups)
			for gr in range(len(groups)):
				d[groups[gr]]=markers[gr]

			for i in range(len(groups)):
				ax.scatter(comp[i,], d[groups[i]],label=groups[i])

		elif dim == 2:
			ax.scatter(comp[:,0],comp[:,1])
			groups=[None]*len(self.labels)
		else:
			ax.scatter(comp[:,0],comp[:1],comp[:2])
			groups=[None]*len(self.labels)			

		fout=open('%s.equivalences'%self.prefix,'w')
		if not MD:
			for l in range(len(self.labels)):
				ax.annotate(l,comp[l,]+0.1,fontsize=fontsize)
				fout.write('%s\t%s\t%s'%(l,self.labels[l],groups[l]))

		if self.type == 'PCA':
			ax.set_xlabel('PC 1', fontsize=fontsize)
			ax.set_ylabel('PC 2', fontsize=fontsize)
			if dim >= 3:
				ax.set_zlabel('PC 3', fontsize=fontsize)
				ax.view_init(30, 45)
		else:
			ax.set_xlabel('Axis 1', fontsize=fontsize)
			ax.set_ylabel('Axis 2', fontsize=fontsize)
			if dim >= 3:
				ax.set_zlabel('Axis 3', fontsize=fontsize)
				ax.view_init(30, 45)
		if groups[0]:
			ax.legend(loc=0, fancybox=True, shadow=True)
		
		if MD:
			initx,inity = comp[:,0][0],comp[:,1][0]
			lastx,lasty = comp[:,0][-1],comp[:,1][-1]
			ax.annotate('Initial conformation', xy=(initx, inity), 
				        xytext= (float(initx)+10, float(inity)+20),
				        arrowprops=dict(facecolor='blue', shrink=0.05, frac=0.15))
				
			ax.annotate('Final conformation', xy=(lastx, lasty),
				        xytext=(float(lastx)+10, float(lasty)+40),
				        arrowprops=dict(facecolor='blue', shrink=0.05, frac=0.15))

		fig.tight_layout()
		plt.show()
		fig.savefig(self.prefix+'_%s.png'%(self.type), dpi=dpi)
		fout.close()


	def PlotXDA(self,membership,group_labels=None,stds=3,ellipses=True,dpi=100,typeof='LDA',fontsize=10,MD=False):
		'''
		Plots a Linear Discriminant Analysis (LDA) or a Quadratic Discriminan Analysis (QDA) with
		confidence ellipses at std (standard deviations)
		'''
		if group_labels:
			target_names = group_labels
		else:
			target_names=list(set(membership))	
		fig = plt.figure()
		ax = fig.add_subplot(111)
		for c, i, target_name in zip(colors, list(set(membership)), target_names):
			sub = self.fit[membership == i, ]
			x=sub[:,0]
			Y=sub[:,1]
			if ellipses:
				for j in xrange(1, stds+1):
					ax.add_artist(self.ellipses[i][j])
				ax.scatter(x, Y, c=c, label=target_name)
		ax.spines['top'].set_color('none')
		ax.xaxis.tick_bottom()
		ax.spines['right'].set_color('none')
		ax.yaxis.tick_left()
		if typeof == 'LDA':
			ax.set_xlabel('LD 1', fontsize=fontsize)
			ax.set_ylabel('LD 2', fontsize=fontsize)
		else:
			ax.set_xlabel('QD 1', fontsize=fontsize)
			ax.set_ylabel('QD 2', fontsize=fontsize)

		if MD:
			initx,inity = self.fit[:,0][0],self.fit[:,1][0]
			lastx,lasty = self.fit[:,0][-1],self.fit[:,1][-1]
			ax.annotate('Initial conformation', xy=(initx, inity), 
		                xytext= (float(initx)+10, float(inity)+20),
		                arrowprops=dict(facecolor='blue', shrink=0.05, frac=0.15))
				
			ax.annotate('Final conformation', xy=(lastx, lasty),
		                xytext=(float(lastx)+10, float(lasty)+40),
		                arrowprops=dict(facecolor='blue', shrink=0.05, frac=0.15))

		plt.show()
		fig.savefig(self.prefix+'_%s.png'%(typeof), dpi=300)

	def ellipse(self, singlegroupx,singlegroupy,std=2,color='k'):
		''' 
		Create an ellipse given points with x coordinates in singlegroupx and singlegroupy
		'''
		cov        = np.cov(singlegroupx, singlegroupy)
		lambda_, v = np.linalg.eig(cov)
		lambda_    = np.sqrt(lambda_)
		width      = lambda_[0]*std*2
		height     = lambda_[1]*std*2
		centerx    = np.mean(singlegroupx)
		centery    = np.mean(singlegroupy)
		angle      = np.rad2deg(np.arccos(v[0, 0]))
		ell        = Ellipse(xy=(centerx,centery), width=width , height=height , angle=angle, 
		                     color=color)
		ell.set_facecolor('none')

		return ell

	def pointsInEllipse(self,Xs,Ys,ellipse):
		'''
		Tests which set of points are within the boundaries defined by the ellipse. The set of points
		are defined in two arrays Xs and Ys for the x-coordinates and y-coordinates respectively
		'''
		inside = []
		outside= []
		for i in range(len(Xs)):
			point = (Xs[i],Ys[i])
			if ellipse.contains_point(point):
				inside.append(point)
			else:
				outside.append(point)
		return inside, outside

	def getEllipses(self,stds):
		'''will populate the ellipses attribute'''
		
		for mem,col in zip(list(set(membership)),colors):
			self.ellipses[mem]={}
			sub = self.fit[membership == mem, ]
			Xs=sub[:,0]
			Ys=sub[:,1]
			for j in xrange(1, stds+1):
				self.ellipses[mem][j]=self.ellipse(Xs,Ys,std=j,color=col)

	def LDA(self,membership,group_labels=None,stds=3,ellipses=True,dpi=100):
		'''
		Perform a Linear discriminant analysis of the data and plot it. Membership must be an array
		of integers of the same lenght of the number of observations in the data. 
		'''
		
		lda = LDA(n_components=2)
		self.fit = lda.fit(self.data, membership).transform(self.data)
		if ellipses:
			self.getEllipses(stds)
		self.PlotXDA(membership,group_labels=group_labels,stds=stds,ellipses=ellipses,
		             dpi=dpi, typeof='LDA')

	def QDA(self,membership,group_labels=None,stds=3,ellipses=True,dpi=100):
		qda = QDA()
		self.fit = qda.fit(self.data, membership).predict(self.data)
		if ellipses:
			self.getEllipses(stds)
		self.PlotXDA(membership,group_labels=group_labels,stds=stds,ellipses=ellipses,
		             dpi=dpi,typeof='QDA')
# END Functions bit###############################################################################
if __name__ == "__main__":
	import optparse,sys
	opts = optparse.OptionParser(usage='%prog <prefix> <GM file> [options]')
	opts.add_option('-s','--std',dest='std', action="store", default=3,type='int', help='Standard '\
	                'deviations to plot ellipses. Has no effect for PCA or any of the MDS.'\
	                'Default:3')
	opts.add_option('-m','--mem',dest='mem', action="store", default=None, help='File name for '\
	                'the membership vector if any of the discriminant analysis is usde. The file'\
	                ' is a space sepatated format, with the groupings')	
	opts.add_option('-t','--type',dest='type', action="store", default='All', help='Type of '\
	                'analysis. Available: classic MDS (PCoA), non-metric MDS (nMDS), Linear'\
	                ' Discriminan Analysis (LDA), Quadratic discriminant analysis (QDA) or PCA.'\
	                ' You can pass All if you want to do all of the above. Default:All')
	opts.add_option('-M','--MD',dest='MD', action="store_true", default=False, help='If too many '\
	                'snapshots in a molecular dynamic simulation are used, this option will stop '\
	                'printing the labels, and will point at the extremes of the trajectory')
	
	options, args = opts.parse_args()
	if options.type == 'All' and not options.mem:
		print 'You choose to use all the functions but did not provide a membership file.'
		sys.exit()
	if options.mem:
		membership = np.array(open(options.mem).read().strip().split())
	O = ORD(args[0], args[1])
	if options.type == 'All':
		PCoA = O.MDS(MD=options.MD)
		nMDS = O.MDS(typeof='non-metric',MD=options.MD)
		PCA = O.PCA(MD=options.MD)
		O.LDA(membership)
		O.QDA(membership)
	elif options.type == 'PCoA':
		PCoA = O.MDS(MD=options.MD)
		
	elif options.type == 'nMDS':
		nMDS = O.MDS(typeof='non-metric',MD=options.MD)
		
	elif options.type == 'PCA':
		PCA = O.PCA(MD=options.MD)
		
	elif options.type == 'LDA':
		O.LDA(membership)
	else:
		O.QDA(membership)		
	
	