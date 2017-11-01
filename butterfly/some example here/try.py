# -*- coding: utf-8 -*-
import os
import shutil
import time
import numpy as np
from subprocess import call as bash

#file
import foamfile
import controlDict
import search


global working_dir
working_dir = os.getcwd()



def clear_dir(dir):
	if os.path.exists(dir):
		shutil.rmtree(dir)
		print('deleted'+dir)
num=0

for water_percent in (0.5,0.7,0.9):

	setFieldDict='''/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  5                                     |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
	version     2.0;
	format      ascii;
	class       dictionary;
	location    "system";
	object      setFieldsDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

defaultFieldValues
(
	volScalarFieldValue alpha.water 0
);

regions
(
	boxToCell
	{
		box (0 0 0) (8 %.2f 0.1);
		fieldValues
		(
			volScalarFieldValue alpha.water 1
		);
	}
);


// ************************************************************************* //'''%(1.5492*water_percent)
	
	for acc in (5.0,8.0):#in m/s^2
		for speed in (10,24):#in m/s
			s0=time.time()
			speed_down_time=round(speed/acc,1)#in s
			stop_time=10
			total_time=speed_down_time+stop_time
			path=working_dir+r'/py/water='+str(water_percent)+'_'+'acc='+str(acc)+'_'+'speed='+str(speed)
			clear_dir(path)
			shutil.copytree(working_dir+r'/0.0',path+r'/0.0')
			shutil.copytree(working_dir+r'/constant',path+r'/constant')
			shutil.copytree(working_dir+r'/system',path+r'/system')

			#setFieldDict
			with open(path+r'/system/setFieldsDict','w') as f:
				f.write(setFieldDict)
			#g
			gFile=foamfile.FoamFile.fromFile(path+r'/constant/g')
			g='(-'+str(acc)+' -9.81 0)'                
			gDict={'value':g}
			gFile.updateValues(gDict)
			gFile.save(path)

			#controlDict
			c=controlDict.ControlDict.fromFile(path+r'/system/controlDict')
			writeInterval=float(c.writeInterval)
			# newEndTime=str(float(c.endTime)+5.0)
			c.setValueByParameter('startTime','0.0')
			c.setValueByParameter('endTime',str(speed_down_time))
			c.save(path)

			s1=time.time()
			print('file_operating takes %.2fs'%(s1-s0))
			#foam
			os.chdir(path)
			with open(path+r'/log_0','w') as log:
				bash('blockMesh',stdout=log)
				bash('setFields',stdout=log)
				bash('interFoam',stdout=log)
			s2=time.time()
			print('speed_down takes %.2fs'%(s2-s1))
			#g
			gFile=foamfile.FoamFile.fromFile(path+r'/constant/g')
			g='(0 -9.81 0)'                
			gDict={'value':g}
			gFile.updateValues(gDict)
			gFile.save(path)

			#stop cal
			c=controlDict.ControlDict.fromFile(path+r'/system/controlDict')
			newStartTime=c.endTime
			newEndTime=str(float(newStartTime)+stop_time)
			c.setValueByParameter('startTime',newStartTime)
			c.setValueByParameter('endTime',newEndTime)
			c.save(path)
			with open(path+r'/log_1','w') as log:
				bash('interFoam',stdout=log)
			os.chdir(working_dir)
			s3=time.time()
			print('calm_down takes %.2fs'%(s3-s2))
			#post_process
			p_data=search.get_v(path+r'/'+str(writeInterval)+r'/p','leftWall')
			for t in np.arange(writeInterval*2,total_time+writeInterval,writeInterval):
				p=search.get_v(path+r'/'+str(t)+r'/p','leftWall')
				p_data=np.vstack((p_data,p))#old on the left/less
			s4=time.time()
			print('numpy takes %.2fs'%(s4-s3))
			#print(p_data.shape)
			np.savetxt(path+r'/p_data',p_data)
			np.savetxt(path+r'/p_max',np.max(p_data,axis=0))
			s5=time.time()
			print('saving_data takes %.2fs'%(s5-s4))
			print('total time:%.2fs'%(s5-s0))

