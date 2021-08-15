# BlockSim-Redact
This is a simple Redactable Blockchain Simulator of my final year project. The work is utillising Discrete Logarithm based Chameleon Hash, Shamir's Secret Sharing Scheme and Ateniese's Chain Redact Algorithm.

# How to Run the Project?

1. I would recommend [PyCharm](https://www.jetbrains.com/pycharm/) as the *IDE* to run the code.
2. Once you have cloned or downloaded the project, open it with PyCharm.
```
git clone
```
3. In an `import` statement of a Python file, click a package which is not yet imported. You can also run the following code to install the packages. [See details](https://www.jetbrains.com/help/pycharm/managing-dependencies.html#apply_dependencies)
```
pip install openpyxl
pip install xlsxwriter
pip install pandas
pip install numpy
```
4. Configure the Python interpreter in PyCharm. [See details](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html)
5. You can explore the modules and packages. 
   - You can try with different parameters in the InputConfig.py file
   - Have a look with the cryptographic schemes in the CH package
   - Results are stored in the Results folder. When storing simulation's results, do aware of the csv output file name
   - Configure the results and statistical parameter in the Statistics.py
   - Models module stores the implementation of the redactable blockchain
6. Run the Main.py to start the simulation.
7. Try with different input parameters and see how the results change. Finally, use the Statistic_Analysis.ipynb (in the Results module) to analysis the simulation results.

# References
This project is inspired by the following works:
- [BlockSim](https://github.com/maher243/BlockSim) 
- [Redactable Blockchain – or – Rewriting History in Bitcoin and Friends](https://ieeexplore.ieee.org/document/7961975)
- [How to Share a Secret](http://web.mit.edu/6.857/OldStuff/Fall03/ref/Shamir-HowToShareASecret.pdf)
- [Discrete logarithm based chameleon hashing and signatures without
key exposure](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.699.7889&rep=rep1&type=pdf)

