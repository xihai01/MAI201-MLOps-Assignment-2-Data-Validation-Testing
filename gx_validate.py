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

# validate def
val_def = context.validation_definitions.add(
  gx.ValidationDefinition(
    name="validate_customers",
    data=batch_def,
    suite=suite
  )
)

# run and save summary as HTML file
results = val_def.run(batch_parameters={"dataframe": df})
print(f"\n{'='*60}")
print(f"  OVERALL SUCCESS: {results['success']}")
print(f"  Total rows validated: {len(df)}")
print(f"{'='*60}\n")

expectations_results = results["results"]

summary = []
for r in expectations_results:
    exp_type  = r["expectation_config"]["type"]
    col       = r["expectation_config"]["kwargs"].get("column", "table")
    success   = r["success"]
    res       = r.get("result", {})

    unexpected_count   = res.get("unexpected_count")
    unexpected_pct     = res.get("unexpected_percent")
    element_count      = res.get("element_count")
    observed_value     = res.get("observed_value")

    status = "PASS" if success else "FAIL"
    label  = f"{col} | {exp_type.replace('expect_', '').replace('_', ' ')}"

    detail = ""
    if unexpected_count is not None:
        detail = f"{unexpected_count} unexpected ({unexpected_pct:.1f}%)"
    elif observed_value is not None:
        detail = f"observed: {observed_value}"

    print(f"  [{status}]  {label}")
    if detail:
        print(f"          {detail}")

    summary.append({
        "column": col,
        "expectation": exp_type,
        "success": success,
        "unexpected_count": unexpected_count,
        "unexpected_percent": round(unexpected_pct, 2) if unexpected_pct is not None else None,
        "element_count": element_count,
        "observed_value": observed_value,
    })

print(f"\n{'='*60}")
passed = sum(1 for s in summary if s["success"])
print(f"  {passed}/{len(summary)} expectations passed")
print(f"{'='*60}\n")

# save to HTML file
# Build a DataFrame from your summary list
summary_df = pd.DataFrame(summary)

# pandas has a built-in .to_html()
html = summary_df.to_html(index=False)

# Wrap in a basic page
html_page = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Validation Results</title>
  <style>
    body {{ font-family: sans-serif; padding: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }}
    th {{ background: #f0f0f0; }}
    tr.fail {{ background: #fdecea; }}
    tr.pass {{ background: #e8f5e9; }}
  </style>
</head>
<body>
  <h1>GX Validation Summary</h1>
  <p>Overall success: {results['success']}</p>
  {html}
</body>
</html>
"""

with open("validation_summary.html", "w") as f:
    f.write(html_page)
