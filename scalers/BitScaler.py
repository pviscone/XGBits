import numpy as np

class BitScaler:
    """
    A class for scaling numerical data using bit scaling. Like min-max but dividing with the smallest power of 2 that covers the range.
    Methods:
    - __init__(): Initializes the BitScaler object.
    - auto_range(df, columns=None): Calculates the range of values for the specified columns in the given DataFrame.
    - fit(range_dict=None, target=(-1, 1)): Fits the scaler to the given range dictionary and target values.
    - apply(df): Applies the scaling functions to the specified columns of the given DataFrame.
    - save(filename): Save the scaler to a file.
    - load(filename): Load the scaler parameters from a file and fit the scaler.
    """

    def __init__(self) -> None:
        """
        Initializes the BitScaler object.
        """
        self.fitted = False
        self.range_dict = None

    def auto_range(self, df, columns=None):
        """
        Calculates the range of values for the specified columns in the given DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame containing the data.
            columns (list, optional): The list of column names to calculate the range for. If not provided, the range will be calculated for all columns in the DataFrame.

        Returns:
            None
        """

        columns = df.columns if columns is None else columns
        self.range_dict = {key: (df[key].min(), df[key].max()) for key in columns}

    def fit(self, range_dict=None, target=(-1, 1)):
        """
        Fits the scaler to the given range dictionary and target values.

        Args:
            range_dict (dict|None, optional): A dictionary containing the range values for each key. Can be None if the range is to be automatically calculated with auto_range. Defaults to None.
            target (tuple, optional): A tuple containing the new low and high values for scaling. Defaults to (-1, 1).

        Raises:
            ValueError: If the scaler is already fitted.
        """

        self.range_dict = range_dict
        assert (
            self.range_dict is not None
        ), "range_dict must be provided or calculated with auto_range"

        if self.fitted:
            raise ValueError("Scaler already fitted")

        self.scale_funcs = {}
        new_low, new_high = target

        for key in self.range_dict:
            low, high = self.range_dict[key]

            quant_range = 2 ** np.ceil(np.log2(high - low))

            #! God damn, python, you suck!!!
            #! Dirty workaround to avoid the lambda function to capture the last value of the loop
            self.scale_funcs[key] = eval(
                f"lambda x: {new_low}+((x-{low})*({new_high}-{new_low})/{quant_range})"
            )

        self.range_dict["target"] = target
        self.target = target
        self.fitted = True

    def apply(self, df):
        """
        Applies the scaling functions to the specified columns of the given DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame to apply the scaling functions to.

        Returns:
            pandas.DataFrame: The DataFrame with the scaled columns.

        Raises:
            ValueError: If the scaler has not been fitted.
        """
        if not self.fitted:
            raise ValueError("Scaler not fitted")
        for key in self.scale_funcs:
            df[key] = self.scale_funcs[key](df[key])
        return df

    def save(self, filename):
        """
        Save the scaler to a file.

        Args:
            filename (str): The name of the file to save the scaler to.

        Raises:
            ValueError: If the scaler is not fitted.

        Returns:
            None
        """
        if not self.fitted:
            raise ValueError("Scaler not fitted")
        np.save(filename, self.range_dict)

    def load(self, filename):
        """
        Load the scaler parameters from a file and fit the scaler.

        Args:
            filename (str): The path to the file containing the scaler parameters.

        Returns:
            None
        """
        self.range_dict = np.load(filename, allow_pickle=True).item()
        target = self.range_dict.pop("target")
        self.fit(self.range_dict, target=target)
