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

# expectations for customer data
suite.add_expectation(
  # customer_id not null
  gx.expectations.ExpectColumnValuesToNotBeNull(
    column="customer_id"
  )
)

suite.add_expectation(
  # customer_id to be unique
  gx.expectations.ExpectColumnValuesToBeUnique(
    column="customer_id"
  )
)

suite.add_expectation(
  # age between 0 - 120
  gx.expectations.ExpectColumnValuesToBeBetween(
    column="age",
    min_value=0,
    max_value=120
  )
)

suite.add_expectation(
  # valid email format
  gx.expectations.ExpectColumnValuesToMatchRegex(
    column="email",
    regex=r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
  )
)

suite.add_expectation(
  # salary present in at least 95% of rows
  gx.expectations.ExpectColumnValuesToNotBeNull(
    column="salary",
    mostly=0.95
  )
)

suite.add_expectation(
  # country must be USA, Canada, UK or Australia
  gx.expectations.ExpectColumnValuesToBeInSet(
    column="country",
    value_set=["USA", "Canada", "UK", "Australia"]
  )
)

suite.add_expectation(
  # signup date must be of datatime type
  gx.expectations.ExpectColumnValuesToMatchRegex(
    column="signup_date",
    regex=r"^\d{1,2}/\d{1,2}/\d{4}$"
  )
)

suite.add_expectation(
  # row count must be between 500 - 1000
  gx.expectations.ExpectTableRowCountToBeBetween(
    min_value=500,
    max_value=1000
  )
)

