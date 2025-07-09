{smcl}
{* *! version 0.1.7 09jul2025}{...}
{viewerjumpto "Syntax" "texiv##syntax"}{...}
{viewerjumpto "Description" "texiv##description"}{...}
{viewerjumpto "Options" "texiv##options"}{...}
{viewerjumpto "Examples" "texiv##examples"}{...}
{viewerjumpto "Installation" "texiv##installation"}{...}
{viewerjumpto "Author" "texiv##author"}{...}
{title:Title}

{p2colset 5 15 17 2}{...}
{p2col :{hi:texiv} {hline 2}}A machine learning–based package for transforming text into instrumental variables (IV){p_end}
{p2colreset}{...}

{marker syntax}{...}
{title:Syntax}

{p 8 15 2}
{cmd:texiv} {varname} {cmd:,} {opt kws(string)}

{marker description}{...}
{title:Description}

{pstd}
{cmd:texiv} is a Python-based Stata toolkit that leverages Stata 16+'s support for Python integration.
It uses machine learning techniques to transform text variables into instrumental variables by analyzing
specified keywords to generate numerical indicators that can be used as instruments.

{pstd}
This command requires that you have properly configured your Python environment and installed the
corresponding Python package.

{marker options}{...}
{title:Options}

{phang}
{opt kws(string)} specifies the keywords to use for text analysis. This is a required option.
Keywords should be separated by spaces and enclosed in quotes.

{marker examples}{...}
{title:Examples}

{pstd}Transform a text variable named {cmd:reports} using digitalization-related keywords:{p_end}
{phang2}{cmd:. texiv reports, kws("digitalization intelligent artificial_intelligence technology_innovation cloud_computing IoT")}{p_end}

{pstd}For Chinese text analysis:{p_end}
{phang2}{cmd:. texiv reports, kws("数字化 智能化 人工智能 科技创新 云计算 物联网")}{p_end}

{pstd}This will create 3 new columns in your dataset with the transformed variables.{p_end}

{marker installation}{...}
{title:Installation}

{pstd}
Install the Stata package:{p_end}
{phang2}{cmd:. github install sepinetam/texiv}{p_end}

{pstd}
Install the Python package:{p_end}
{pstd}
You need to find the Python that is integrated with Stata, then install the package using pip.
For detailed instructions, please refer to:{p_end}

{pstd}
For Windows users: See {browse "https://www.stata.com/features/overview/pystata-python-integration":Stata Official Guide}{p_end}

{pstd}
For macOS users:{p_end}
{phang2}1. Use {cmd:python query} to find the Python path{p_end}
{phang2}2. Run in terminal: {cmd:sudo -H /path/to/python3 -m pip install --upgrade texiv}{p_end}

{pstd}
For users in China, use the Tsinghua mirror:{p_end}
{phang2}{cmd:sudo -H /path/to/python3 -m pip install --upgrade texiv -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn}{p_end}

{pstd}
For first-time use, you should configure your embedding model and type. For more information,
please refer to the project README.

{marker author}{...}
{title:Author}

{pstd}Song Tan{break}
Email: sepinetam@gmail.com{break}
Project: {browse "https://github.com/sepinetam/texiv":https://github.com/sepinetam/texiv}{p_end}

{pstd}
License: MIT{break}
Bug Reports: {browse "https://github.com/sepinetam/texiv/issues/new":GitHub Issues}{p_end}