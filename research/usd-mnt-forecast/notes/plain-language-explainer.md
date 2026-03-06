# Plain-Language Explainer

## What does "random walk" mean?

It means the simplest forecast is just: next month will probably look a lot like this month.

That sounds almost silly, but for exchange rates it is a very serious benchmark. Many fancy models fail to beat it.

## What does it mean when a model "beats random walk"?

It means the model made smaller forecasting mistakes than the simple no-change rule.

If a model's RMSE ratio versus random walk is:

- below `1.0`, the model did better
- above `1.0`, the model did worse

So a ratio of `0.57` means the model's forecast errors were about `43%` smaller than the random-walk benchmark in that test window.

## Why use lagged data?

Because otherwise the model can cheat.

If you use data that was only published later, the backtest stops being realistic. A good forecasting study has to ask:

"What would someone have known at the time?"

That is why this project shifts monthly and quarterly macro data backward before modeling.

## What is a coefficient telling us?

In a linear model, a coefficient tells us the direction of the relationship inside that model.

Very roughly:

- positive sign: higher values of that feature tend to go with higher future `USD/MNT`
- negative sign: higher values of that feature tend to go with lower future `USD/MNT`

Since higher `USD/MNT` means a weaker tugrik, you can translate the sign into ordinary language.

## Why do some signs look strange?

Because macro variables move together.

For example:

- commodity prices move together
- the exchange rate and inflation can influence each other
- reserves, capital flows, and intervention are connected

So one coefficient is not a pure law of nature. It is the model's best attempt to separate overlapping signals in a limited sample.

## What does a confidence interval mean here?

It is a range that says: based on past forecasting misses, the future value could plausibly fall somewhere in this band.

It does **not** mean:

- the exchange rate will stay inside the band for sure
- the model understands the economy perfectly

It means:

- the center line is the model's best guess
- the band shows how uncertain that guess is

## Why compare USD/MNT and CNY/MNT?

Because it tells us whether the forecasting signal is really about the dollar or about broader external conditions.

If only `USD/MNT` worked, the story might be mostly about global dollar cycles.
If `CNY/MNT` also works, the story is probably broader: trade structure, regional currency conditions, and Mongolia's own balance-of-payments dynamics.

## What is the simplest way to explain the result?

A good plain-language summary is:

`The tugrik is not easy to forecast month to month, but Mongolia's macro data does contain useful clues, especially once you look a few months ahead instead of just one month ahead.`
