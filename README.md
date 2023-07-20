# tap-edgar

Singer tap for SEC EDGAR filings.

## One-time setup

    script/bootstrap

## Run tests
    
    script/test

## Extract S&P 500 data 

    poetry run tap-edgar --config config/sp500.config.json >output/sp500.output.jsonl