import great_expectations as gx
import pandas as pd

# load the existing file based context
context = gx.get_context(mode="file")

# connect to your data
df = pd.read_csv("customer_data.csv")

# establish a connection to pandas, where we will fetch data
data_source = context.data_sources.add_pandas('data_source')
data_asset = data_source.add_dataframe_asset('data')

# validate everything at once
batch_def = data_asset.add_batch_definition_whole_dataframe("all_rows")

# validate on runtime
batch = batch_def.get_batch(batch_parameters={"dataframe": df})

# create an expectation suite
suite = context.suites.add(gx.ExpectationSuite(name="customer_data_expectations"))
