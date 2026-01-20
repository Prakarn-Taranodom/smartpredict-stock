# Alpha Vantage API Setup for Render

## Step 1: Get Free API Key

1. Go to https://www.alphavantage.co/support/#api-key
2. Enter your email
3. Click "GET FREE API KEY"
4. Copy your API key (looks like: `ABCD1234EFGH5678`)

## Step 2: Set Environment Variable in Render

1. Go to your Render Dashboard
2. Select your `smartpredict-stock` service
3. Click **Environment** in the left sidebar
4. Click **Add Environment Variable**
5. Set:
   - **Key**: `ALPHA_VANTAGE_API_KEY`
   - **Value**: `YOUR_API_KEY_HERE` (paste your key)
6. Click **Save Changes**
7. Render will automatically redeploy

## Step 3: Verify

After deployment completes:
- Try predicting a stock (e.g., AAPL, MSFT)
- Check logs for any errors

## API Limitations (Free Tier)

- **25 requests per day**
- **5 API calls per minute**
- Sufficient for demo/testing
- For production, upgrade to paid plan

## Supported Tickers

- US stocks: AAPL, MSFT, GOOGL, TSLA, etc.
- Crypto: BTC-USD, ETH-USD (use format: BTCUSD, ETHUSD)
- Thai stocks (.BK): Not supported by Alpha Vantage

## Alternative: Use Demo Mode

If you don't want to use Alpha Vantage, the app will automatically use synthetic demo data when API key is not set.

## Troubleshooting

**Error: "ALPHA_VANTAGE_API_KEY not found"**
- Make sure you added the environment variable in Render
- Check spelling: `ALPHA_VANTAGE_API_KEY` (case-sensitive)
- Redeploy after adding the variable

**Error: "API rate limit exceeded"**
- Free tier: 25 requests/day, 5 requests/minute
- Wait a few minutes and try again
- Consider upgrading to paid plan

**Error: "Invalid ticker symbol"**
- Alpha Vantage only supports US stocks
- Thai stocks (.BK) are not available
- Use US tickers: AAPL, MSFT, GOOGL, etc.
