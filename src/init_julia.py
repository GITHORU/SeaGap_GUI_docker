from juliacall import Main as jl
from juliacall import Pkg as jlPkg

jlPkg.add(url="https://github.com/f-tommy/SeaGapR")
jl.seval("using SeaGapR")
