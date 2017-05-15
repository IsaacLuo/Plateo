from ..tools import infer_plate_size_from_wellnames, number_to_rowname
import pandas as pd
from plateo.containers import get_plate_class

def plate_from_dataframe(dataframe, wellname_field="wellname",
                         num_wells="infer", data=None):
    """Create a plate from a Pandas dataframe where each row contains the
    name of a well and data on the well.

    it is assumed that the dataframe's index is given by the well names.

    This function is used e.g. in `plate_from_list_spreadsheet`.

    Parameters
    ----------

    dataframe
      A Pandas dataframe

    wellname_field
      The name of the Pandas dataframe column indicating the name of the wells.

    num_wells
      Number of wells in the Plate to be created. If left to default 'infer',
      the size of the plate will be chosen as the smallest format (out of
      96, 384 and 1536 wells) which contains all the well names.

    data
      Metadata information for the plate.
    """

    # TODO: infer plate class automatically ?

    dataframe = dataframe.set_index(wellname_field)
    wells_data = {
        well: row.to_dict()
        for well, row in dataframe.iterrows()
    }
    if num_wells == "infer":
        num_wells = infer_plate_size_from_wellnames(wells_data.keys())
    plate_class = get_plate_class(num_wells=num_wells)
    return plate_class(wells_data=wells_data, data=data)


def plate_from_list_spreadsheet(filename, sheetname=0, num_wells="infer",
                                wellname_field="wellname"):
    """Create a plate from a Pandas dataframe where each row contains the
    name of a well and metadata on the well.


    Parameters
    ----------

    filename
      Path to the spreadsheet file.

    sheetname
      Index or name of the spreadsheet to use.

    num_wells
      Number of wells in the Plate to be created. If left to default 'infer',
      the size of the plate will be chosen as the smallest format (out of
      96, 384 and 1536 wells) which contains all the well names.

    wellname_field="wellname"
      Name of the column of the spreadsheet giving the well names
    """

    if ".xls" in filename:  # includes xlsx
        dataframe = pd.read_excel(filename, sheetname=sheetname)
    elif filename.endswith(".csv"):
        dataframe = pd.read_csv(filename)
    return plate_from_dataframe(dataframe, wellname_field=wellname_field,
                                num_wells=num_wells,
                                data={"filename": filename})

def plate_from_platemap_spreadsheet(filename, data_field="info",
                                    num_wells="infer", headers=True,
                                    skiprows=None):
    if filename.lower().endswith(".csv"):
        file_type = "csv"
    else:
        file_type = "xlsx"
    with open(filename, 'rb') as file_handle:
        plate_from_platemap_spreadsheet_file(file_handle, file_type, filename, metadata_field, num_wells, headers, skiprows)

def plate_from_platemap_spreadsheet_file(file_handle, file_type="csv", filename="unknown", metadata_field="info", num_wells="infer", headers=True, skiprows=None):
    """Parse spreadsheets representing a plate map.

    The spreadsheet should be either a 8 rows x 12 columns csv/excel file,
    or have headers like this

    .. code:: bash

          1  2  3  4  5  6  7  8  9  10 11 12
       A  .  .  .  .  .  .  .  .  .  .  .  .
       B  .  .  .  .  .  .  .  .  .  .  .  .
       C  .  .  .  .  .  .  .  .  .  .  .  .
       D  .  .  .  .  .  .  .  .  .  .  .  .
       E  .  .  .  .  .  .  .  .  .  .  .  .
       F  .  .  .  .  .  .  .  .  .  .  .  .
       G  .  .  .  .  .  .  .  .  .  .  .  .
       H  .  .  .  .  .  .  .  .  .  .  .  .
    """

    index_col = 0 if headers else None
    if file_type == "csv":
        dataframe = pd.read_csv(file_handle, index_col=index_col,
                                header=index_col, skiprows=skiprows)
    else:
        dataframe = pd.read_excel(file_handle, index_col=index_col,
                                  header=index_col, skiprows=skiprows)
    if headers:
        wells_data = {
            row + str(column): {data_field: content}
            for column, column_content in dataframe.to_dict().items()
            for row, content in column_content.items()
        }
    else:
        wells_data = {
            number_to_rowname(row + 1) + str(column + 1):
                {data_field: content}
            for column, column_content in dataframe.to_dict().items()
            for row, content in column_content.items()
        }
    if num_wells == "infer":
        num_wells = infer_plate_size_from_wellnames(wells_data.keys())
    plate_class = get_plate_class(num_wells=num_wells)
    return plate_class(wells_data=wells_data,
                       data={"file_source": filename})
