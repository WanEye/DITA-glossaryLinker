# DITA-glossaryLinker
# Links to glossary terms

This utility adds tags `<xref>` to DITA files to link to glossary items, items with `<glossentry>` and `<glossdef>`.

You need the following files.
1. `glossaryLinker.py`
2. DITA files in the same directory or in the subdirectories.

To run the utility, you need Python. The utility works with Python version 2.7.14.

## Prereqs for the glossary files.
* DOCTYPE! glossgroup
* The glossary.dita file has the folowing structure.
```
    <glossentry id="">
        <glossterm/>
        <glossdef/>
        
    </glossentry>
    
    <glossentry id="">
    ...    
    </glossentry>
```

See the sample project for an example. 

## Contents

* `DITAtest` folder with sample DITA project
* `DITAtest.zip` archive file of the sample DITA project
* `glossaryLinker.jpg` Jackson diagram of the program structure
* `glossaryLinker.py` Python code

## Output
* Log file that contains information about the routines that the program ran.
* Backup of the original DITA files.
* Changes DITA files with xref tags. 


## Generating the cross reference links 

### Before you begin
1. Verify that Python is installed and works from the DITAMAP directory.

#### To verify:
  
  1. Open a command line. For Windows: start cmd. For Linux: Ctrl + Alt + t. For Mac: Terminal.
  2. Navigate to the directory where your DITAMAP sits.
  3. Type `python --version`. 
 #### Result 
 If you see `Python <version>`, Python works properly.
  
### Procedure
1. Navigate to the directory where your DITAMAP file sits.
3. Copy `glossaryLinker.py` to the directory where your DITAMAP file sits. 
4. Type `python glossaryLinker.py`.

#### Result
* The DITA files contains xref tags.
* In the DITA output, every occurence of a word from every glossary items links to the entry in the glossary.




