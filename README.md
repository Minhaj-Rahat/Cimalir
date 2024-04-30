# Cimalir
This repo contains the implementation code for ["CIMALIR: Cross-Platform IoT Malware Clustering
using Intermediate Representation"](https://ieeexplore.ieee.org/abstract/document/10427663) published in IEEE CCWC 2024. If you use this work please cite the paper.
# Documentation
- Create an object for MalAnalyzer class, specify the Ghidra headless executable path
- Check whether any binary is packed using *check_upx_packer()* and unpack those binaries
- We need to import the binaries in Ghidra and export the JSON database file using *ghidra_import()*, which will be used for similarity analysis
- Check samples in database using *check_pcode_length()* and remove any database files containing zero P-Code due to Ghidra error.
- Before creating similarity matrix feature, we use *optimize_ga()* optimizer which will give us the optimal values for different parameters that we need to sett before calculating similarity matrix.
- Create Similarity Matrix using *create_similarity_matrix(()*
- For BinDiff, we first need to export the binaries using IDA pro and BinExport module. Use *ida_export_bindiff()*
- Then use *similarity_matrix_bindiff* to create similarity matrix file for bindiff
- We need to create string feature file using *create_yara_dict()*
- Before clustering, use *hdbscan_optimal()* for optimal parameters and then use *cluster()* for clustering
# Cite
If you use this work please cite the paper:
```
@INPROCEEDINGS{10427663,

  author={Rahat, Minhajul Alam and Banerjee, Vijay and Bloom, Gedare and Zhuang, Yanyan},

  booktitle={2024 IEEE 14th Annual Computing and Communication Workshop and Conference (CCWC)}, 

  title={Cimalir: Cross-Platform IoT Malware Clustering using Intermediate Representation}, 

  year={2024},

  volume={},

  number={},

  pages={0460-0466},

  keywords={Privacy;Codes;Runtime;Instruction sets;Malware;Internet of Things;Security;IoT;malware;intermediate representation},

  doi={10.1109/CCWC60891.2024.10427663}}

```
