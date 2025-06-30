*!  texiv.ado  -*- ado -*-
/*
Author  : Song Tan (谭淞)
Email   : sepinetam@gmail.com
ProjAdd : https://github.com/sepinetam/texiv
Version : 0.1.2
*/
capture program drop texiv
program texiv
    version 17
    syntax varname, kws(string)

	gettoken var_name : varlist

	// use the python function
	python: texiv_in_stata("`var_name'", "`kws'")
end


version 17
python:
from sfi import Data
from texiv import StataTexIV

def texiv_in_stata(var_name, kws):    StataTexIV().texiv(Data, var_name, kws)

end
