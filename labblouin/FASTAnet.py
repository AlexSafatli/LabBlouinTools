''' A simple parser and writer for FASTA sequence files that uses a rich object hierarchy. '''

# Date:   May 15 2013
# Author: Alex Safatli
# Email:  safatli@cs.dal.ca

import numpy as np

class FASTAsequence:

    def __init__(self,name,seq):

        ''' Initialize this object. Provide a name for the sequence
        and the sequence itself as parameters. '''

        self.name         = name
        self.sequence     = seq
        self.__fastaseq__ = '\n'.join([x for x in self])

    def __iter__(self):

        ''' Iterate through a sequence in a pseudo-line-by-line 
        manner as if it was read in a FASTA file. '''

        s = self.sequence
        for i in xrange(0,len(s),70): yield s[i:i+70]

    def __hash__(self):

        return self.sequence.__hash__()

    def __eq__(self,o):

        return self.sequence == o.sequence

    def __ne__(self,o):

        return not self.__eq__(o)

    def __getitem__(self, item):

        return self.sequence

    def count(self,item):

        ''' Return the number of characters in the sequence equal to input string. '''

        return self.sequence.count(item)

    def removeGaps(self):

        ''' Modify the sequence so gaps are removed and return it. '''

        self.sequence = self.sequence.replace('-','').replace('.','')
        return self.sequence
    
    def gapLess(self):
        
        ''' Return an ungapped sequence without modifying the instance'''
        return self.sequence.replace('-','').replace('.','')
    
    def toUpper(self):

        ''' Modify the sequence so it is uppercase and return it. '''

        self.sequence = self.sequence.upper()
        return self.sequence    

    def toLower(self):

        ''' Return a lowercase version of the sequence, also changing it
        in the structure. '''

        self.sequence = self.sequence.lower()
        return self.sequence            

    def toIndices(self):
        '''transoform a gapped sequence into indices matrix'''
        count=0
        newseq=[]
        for i in self.sequence:
            if (i == '-') or (i == '.'):
                newseq.append(i)
            else:
                newseq.append(count)
                count+=1
        self.Indexseq = ''.join([str(x) for x in newseq])
        return newseq
    
    def __len__(self):

        return len(self.sequence)

    def __str__(self):

        return '>%s\n%s\n' % (self.name,self.__fastaseq__)

class FASTAstructure:

    def __init__(self,filein='',uniqueOnly=True,curate=False):

        ''' A file to be read is optional. If uniqueOnly is set to
        false, multiple duplicate sequences are allowed; otherwise,
        duplicates are ignored and their aliases are recorded in sequence
        Names. If curate is triggered, will remove special characters
        from names. '''

        self.sequences        = {}
        self.orderedSequences = []
        self.sequenceNames    = {}
        self.full             = {}
        self.uniqueOnly       = uniqueOnly
        self.curate           = curate
        self.matrix           = None

        if filein:
            # First, try to read in a path. Otherwise,
            # read in the string comprising the content
            # of a file.
            try: self.readFile(filein)
            except: self.read(filein.split('\n'))

    def getSequenceNames(self):    return self.sequenceNames.values()
    def getSequenceLengths(self):  return [seq.__len__() for seq in self.sequences]
    def getSequences(self):        return self.orderedSequences
    def getSequenceByName(self,n): return self.sequenceNames[n]

    def getStrictlyUngappedPositions(self,seqInds=None,absolutepos=False):

        ''' Acquire the positions of all strictly ungapped sites. If parameter
        is set, expects a list of what sequences (by index) you are checking. 
        Defaults to all sequences Abosulutepos will return also a dictionary of
        the indices in the ungap sequence'''

        if seqInds == None:
            seqInds = range(len(self.sequences))
        seqs = self.orderedSequences
        mask = {}
        posv = []
        abso = {}
        for n in seqInds:
            seq = seqs[n].sequence
            name = seqs[n].name
            mask[n] = []
            abso[name] = []
            for i in xrange(len(seq)):
                char = seq[i]
                if char.isalpha(): 
                    mask[n].append(True)
                    abso[name].append(i)
                else: 
                    mask[n].append(False)
                    abso[name].append(None)
                    
        alnlen = len(mask.values()[0])
        for pos in xrange(alnlen):
            homologous = True
            for key in mask:
                if not mask[key][pos]:
                    homologous = False
                    break
            if homologous: posv.append(pos)       
        if absolutepos: return posv, abso
        else: return posv

    def findAlignedResidueIndices(self):

        ''' Find the indexes of aligned residues in all sequences. return this as a list of indexes '''

        seqlist = self.getSequences()

        seq1 = seqlist[0]
        for seq in seqlist:
            if seq1.__len__() != seq.__len__():
                raise ValueError('Error: These sequences are not all the same length. Perform an alignment')

        self.matrix = np.zeros((len(seqlist),seqlist[0].__len__()))
        seqs = [s.sequence for s in seqlist]

        for i in range(len(seqs)):
            for j in range(len(seqs[i])):
                if seqs[i][j] == '-' or seqs[i][j] == '.':
                    self.matrix[i][j] = 0
                else:
                    self.matrix[i][j] = 1

        aligned = np.where(self.matrix.sum(axis=0) == len(seqs))[0].tolist()

        return aligned

    def readFile(self,fin):

        ''' Read a file in. Return this FASTA object. '''

        fi = open(fin)
        fast = fi.read()
        fi.close()
        self.read(fast.split('>'))#self.read(fast.split('\n'))
        return self

    def read(self,fast):

        ''' Read the contents of a FASTA file. '''
        for fas in fast:
            if fas == '': continue
            bl = fas.split('\n')
            name = bl[0].strip().strip('>')
            seq = ''.join(bl[1:])
            if self.curate:
                tmp = name
                for c in name:
                    if not c.isalnum():
                        tmp = tmp.replace(c,"",1)
                name = tmp 
            self.addSequence(name, seq)
        '''
        name, seq = '', ''
        for line in fast:
            lineC = line.strip()
            if lineC.startswith('>'):
                # add last collected entry
                if name and seq: self.addSequence(name,seq)
                name, seq = (lineC.strip('>')), ''
                if self.curate:
                    tmp = name
                    for c in name:
                        if not c.isalnum():
                            tmp = tmp.replace(c,"",1)
                    name = tmp         
            else: seq += lineC
        if name and seq: self.addSequence(name,seq)    
        '''

    def writeFile(self,fout):

        ''' Write the information currently contained in the
        FASTAstructure to a file as a FASTA-formatted file. '''

        f = open(fout,'w')
        f.write(str(self))
        f.close()

    def addSequence(self,name,seq):

        ''' Add a sequence to the FASTA object. '''

        # Ensure not already in list with
        # a different or same name.
        f = FASTAsequence(name,seq)
        seqs = self.sequences.values()
        self.full[name]=seq
        if name not in self.sequences:
            if (f not in seqs or not self.uniqueOnly):
                self.sequences[name] = f
                self.orderedSequences.append(f)
                self.sequenceNames[f] = [name]
            else:
                # Get that instance of FASTAsequence.
                f = [x for x in seqs if f == x][0]
                self.sequenceNames[f].append(name)
        else:
            print name

    def renameSequence(self,oldname,newname):

        ''' Renames a given sequence. '''

        if oldname in self.sequences:
            f = self.sequences[oldname]
            f.name = newname
            del self.sequences[oldname]
            self.sequences[newname] = f
            self.sequenceNames[f] = newname
        else: raise IndexError('Could not find that name among sequences.')

    def removeSequence(self,name):

        ''' Remove a sequence from the FASTA object and
        return it; or return None if it was not found. '''

        if name in self.sequences:
            f = self.sequences[name]
            index = [i for i, x in enumerate(self.orderedSequences) if x.name == name]
            self.orderedSequences.pop(index[0])#.remove(f)
            del self.sequences[name]
            del self.sequenceNames[f]
            return f
        else: return None

    def reorderSequences(self,iterable):

        ''' Reorder all sequences by an iterable sequence
        of their names. '''

        if len(iterable) != len(self.sequences):
            raise ValueError('Mismatch of length with sequence list.')
        neworder = []
        for it in iterable:
            if it in self.sequences: neworder.append(self.sequences[it])
            else:
                raise KeyError('Could not find %s among sequence names.'% (it))
        self.orderedSequences = neworder

    def removeGaps(self):

        ''' Remove the gaps for all sequences. '''

        s = self.sequences
        for seq in s: 
            nseq = s[seq].removeGaps()
            self.sequences[seq] = nseq

    def allUpper(self):

        ''' Change all sequences to uppercase. '''

        s = self.sequences
        for seq in s: s[seq].toUpper()

    def allLower(self):

        ''' Change all sequences to lowercase. '''

        s = self.sequences
        for seq in s: s[seq].toLower()

    def __iter__(self):

        ''' Iterate through the FASTA by going through
        its sequences. '''

        for seq in self.sequences: yield self.sequences[seq]

    def __len__(self):

        ''' Return the number of sequences in the FASTA object. '''
        if self.uniqueOnly: return len(self.sequences)
        else: return len(self.full.keys())

    def __str__(self):

        ''' Return the FASTA object as FASTA file text content. '''

        return ''.join([str(x) for x in self.orderedSequences])

# Debugging

if __name__ == "__main__":
    import sys
    myfasta = FASTAstructure(sys.argv[1], uniqueOnly=False)
    print myfasta.sequenceNames