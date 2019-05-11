#!/usr/bin/env python
import sys
import time

# Do not have a view active on moneydance 2017 that needs to be refreshed if the history changes it will lock up. use the reminders view it is pretty static.
# update .. the above does not seem to happen on MD 2019
# the import data files should be manually down loaded from www.stockwatch.com and be placed in the directory /opt/moneydance/scripts/tmp/Stockwatch
# goto www.stockwatch.com and click on quotes->download quotes-> enter Symbol -> select year -> select csv format -> submit
# you must have a stockwatch account and be logged in
# one file per security . can be all the dailey close values for that security for one year . file name can be anything that ends in .csv
# this program processes all the .csv files in this directory and moves them to /opt/moneydance/scripts/tmp/Done
# the /opt/moneydance/scripts/tmp part of the directory name is defined in the definitions.py script
# Tested on Tsx , New York and Canadian Mutual funds 
# The Canadian mutual fund symbols that stockwatch uses are different than what is used by most sites . 
# the StockwatchSymbols list in definitions.py must be filled in to convert the symbols 
# example 'TML202':'BIF*CDN',  my moneydance symbol is TML202 . Stockwatch uses BIF*CDN for this same fund.
# stock symbols are automaticly converted by this program from AAA.AA.A to AAA-AA-A-T or AAA-AA-A-N
# ie the stockwatch dots are converted to GlobeIvestor dashes and the exchange is tacked on the end -T is TSX -N is newyork
# <ticker>	<date>	   <exchange>	<open>	<high>	<low>	<close>	<change>	<vol>	<trades>
# BRN*GLO	20141117	F	10.9856	10.9856	10.9856	10.9856	 -0.01	          0	0
# the above is the standard ASCII csv format produced by Stockwatch
# 
# Exchange codes used by Stockwatch
# Code 	Region 	Exchange
# U 	US 	Special code that matches any US symbol
# C 	Canada 	Special code that matches any Canadian symbol
# Z 	US 	Composite feed including the New York and American exchanges -- confirmed GlobeInvestor uses -N
# Q 	US 	Nasdaq, OTCBB, Pink Sheets and Other OTC
# O 	US 	OPRA - US Options
# S 	US 	S&P indexes
# P 	US 	PBOT indexes
# B 	US 	CBOE indexes
# I 	US 	Non-exchange and other indexes such as Dow Jones, Russel, Longon Gold Fix
# T 	Canada 	TSX - Toronto Stock Exchange -- confirmed same as GlobeInvestor
# V 	Canada 	TSX Venture Exchange
# M 	Canada 	Montreal Exchange
# C 	Canada 	CSE
# F 	Canada 	Canadian Mutual Funds  -- confirmed
# E is NEO

# on the jython270 console run ----->>>execfile("updateHistoryStockwatch.py") or use runscripts.py after you down load the history 
# issue #1 stockwatch doesn't use fundserv mutual fund numbers so we have to convert them . example BIP151 = BRN*GLO
# issue #2 stockwatch is missing the mutual fund GOC309
# issue #3 it seems to overload moneydance and lock it up. added a sleep to slow it down. but still locks uo. maybe make sure you don't have a graph on display in moneydance use reminders page
# the above seemed to work . I removed the sleep .. looks like moneydance was trying to update the view as the history was being updated.
# MD 2019 seems to not have this problem

class updateHistoryStockwatch:
   import glob
   import sys
   execfile("/opt/moneydance/scripts/definitions.py")
   
  
   def setPriceForSecurity(symbol, price2, dateint , volume2 , high2 , low2 ): # this version is the latest Dec 29 2017

     root = moneydance.getRootAccount()
  ##   currencies = root.getCurrencyTable() fix from roywsmith
     AcctBook = root.getBook() 
     currencies = AcctBook.getCurrencies()
     if price2 != 0:
       price2 = 1/price2
     else:
       print "Error Zero Price found Skipping it"
       return
     if low2 != 0:
       low2   = 1/low2
     else:
       low2 = price2
     if high2 != 0:
       high2  = 1/high2
     else:
       high2 = price2 
     security = currencies.getCurrencyByTickerSymbol(symbol) #returns a CurrencyType
     if not security:
       print "No security with symbol/name: %s"%(symbol)
       return
     if dateint:
       snapshot = security.setSnapshotInt(dateint, price2) # this returns a CurrencyType.Snapshot
       security.setUserRate(price2)
       snapshot.setDailyVolume (long(volume2) )
       snapshot.setUserRate ( price2 )
       snapshot.setUserDailyHigh ( high2 )
       snapshot.setUserDailyLow ( low2 )
       security.setSnapshotInt(dateint, price2).syncItem() # added this April 19 2019 for change in MD2019 see note below
     else:  
       print "No Date for symbol/name: %s"%(symbol)
     
#     print price2,volume2,high2,low2
     print "Successfully set price for %s"%(security)	    	      
 
# words of wisdom from Sean Reilly on Jan 02 2019 
#Ah yes, sorry about that. We moved a while ago to requiring a sync/save call for snapshots to prevent an overflow of history entries which were coming from 
#calls to create snapshots which weren't meant to be saved. Anyway, you should just change any calls to security.setSnapshotInt(dateint, price) to 
#change any calls to security.setSnapshotInt(dateint, price) to invoke syncItem() on the result: security.setSnapshotInt(dateint, price).syncItem().
#I'll update the sample code now too.
   
	    	      
   
   files = glob.glob(definitions.directory+'Stockwatch/*.csv') # open the directory to be processsed 
   
#   print files

   count = 0
   
   for fle in files:
    ++count 
    fin = open(fle,'r')
#      with open(fle) as fin:
#      fin = open(fle,'r')
#	sym = fin.readline() # disgard the first line its a header
#	print sym            # print the header           
       
   
   
#   fin = open(definitions.directory+'Stockwatch.csv','r') # could use a hard coded file location  /opt/moneydance/scripts/tmp
    print fle   
    sym = fin.readline() # disgard the first line its a header
    print sym            # print the header           

    while 1:
       sym = fin.readline()
       if len(sym) <= 0:
         break
#       sym = sym.replace(',',' ') # strip out all the comma s
     
       lst = sym.split(",") # chop it up into 10 fields    

   #  print lst[0] #ticker
   #  print lst[1] #date
   #  print lst[2] #exchange
   #  print lst[3] #open
   #  print lst[4] #high
   #  print lst[5] #low
   #  print lst[6] #close
   #  print lst[7] #change
   #  print lst[8] #volume
   #  print lst[9] #trades
       if lst[2] == 'F':
          print 'Its a Mutual Fund' # so we need to look up the symbol
          tickerSym = None
          Description = lst[0]
#        Description = Description[:10] #20 was too long try 10 characters
#        print "DESC=", Description
     
          for fundsym , fundname in definitions.StockwatchSymbols.items():  # use the list in definitions to look up the ticker
#        print fundsym , fundname
#        print len(fundname)
	     if len(fundname) <= 0: break
	     if  fundname.count (Description) > 0:
#	     print "found it", fundsym ,fundname
	       tickerSym = fundsym
#	     print "found tickerSym=",tickerSym
	       break
          if tickerSym == None:	
	     print "updateHistoryStockwatch.py Ticker symbol Look up failed ------------------------"
	     break
       else : 
         tickerSym = lst[0] # need to add a -T to the end of it to match the Globeinvestor standard
         tickerSym = tickerSym.replace('.','-')  #  sym = sym.replace(')',' ')  Stockwatch uses dots but GlobeInvestor uses dashes
         if lst[2] == 'T':
             tickerSym = tickerSym+'-T' # if its the TSX
         if lst[2] == 'Z':    
             tickerSym = tickerSym+'-N' # if its the NewYork  Stockwatch=Z and GlobeInvestor=N differ here  
         if lst[2] == 'V':    
             tickerSym = tickerSym+'-X' # Toronto Venture Exchange Stockwatch=V GlobeInvestor=X  TMX=TSXV   
         if lst[2] == 'E':    
             tickerSym = tickerSym+'-NEO' # NEO ATS  TMX=shows both AQL and AQN (AQL is high speed normal trading .AQN is NEO(slow filtered trading))
                                          # stockwatch shows them as E and U , GlobeInvestor just blows up.
             
       volume = long (lst[8])  
       high = float ( lst[4] )
       low =  float  ( lst[5])
# --------------- looks like the date is already in the right format 
     
       number = int( lst[1] ) # this is the date
#     print tickerSym,float(lst[6]),number,volume,high,low
       setPriceForSecurity(tickerSym,float(lst[6]),number , volume , high , low )            # this is a local function
       print tickerSym,float(lst[6]),number,volume,high,low
#      time.sleep(1) # moneydance was freezing up this seemed to help. moneydance will not run while this program is running?? (around 250 values per year per symbol.
#     break 
#   print fle+" time to move it"  # fle has a full path
    dest = fle
    dest = dest.replace('/',' ')
    dest = dest.strip()
    lst = dest.split()
    filename = lst[len(lst)-1]
#   print filename
    import os
    print definitions.directory+'Done/'+filename
    os.rename(fle, definitions.directory+'Done/'+filename) # opt/moneydance/scripts/tmp/Stockwatch/Stockwatch6.csv
    
   if count == 0:  
     print"There are no files to process"
     print"You have to down load them manually"
     print"Save them as /opt/moneydance/scripts/tmp/Stockwatch/anyname.csv"
     print"One file for each Symbol" 
     print"One year of Closing prices in each file"
#     sys.stderr.write("this is a test\n") # didn't work
#     print >>sys.stderr, "another test" # didn't work
#     sys.stdout.write("yet another test\n") # didn't work
#     time.sleep(30)                                        sleep puts moneydance to sleep too 
     #wait = input("PRESS ENTER TO CONTINUE.") # this messed up everything . moneydance froze . had to kill java 
   else:
     print "files processed=",count
     
   print "Done updateHistoryStockwatch.py"

