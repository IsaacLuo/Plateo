"""Parser for qPCR files.

"""

import pandas as pd
from ..tools import index_to_wellname

def parse_qPCR_file(filename):
    dataframe = pd.read_csv(filename, sep="\t", header=3, index_col=False)
    num_wells = dataframe.No.max()
    return {
        index_to_wellname(row.No, num_wells, direction="row"): {
            column: row[column]
            for column in dataframe.columns
        }
        for i, row in dataframe.iterrows()
    }
