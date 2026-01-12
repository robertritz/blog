---
layout: post
title: What happens if you pay people to get married?
date: 2021-10-20 00:00:00 +0800
image: '/images/marriage-spike/cover.jpg'
tags: [marriage, government]
---

We often think of marriage as a serious thing. When you marry someone, most people believe that it will be a lifelong commitment. From much research in many countries, we know that there are many benefits to being married, from living longer to lower insurance rates.

Therefore it makes sense that the government, and society, would want to encourage people to get married. So, what if you offered people the equivalent of $500 to get married? Would existing couples "on the fence" decide to take the plunge? Would people in need of quick cash make a sham wedding?

From 2006-2009, the Mongolian government did precisely this kind of [cash giveaway for new marriages](http://archive.olloo.mn/modules.php?name=News&file=article&sid=30855). Any couple registering a new marriage was eligible for this money, equivalent to roughly 4 months the average Mongolian salary from 2006. The results were nothing short of remarkable.

![](/images/marriage-spike/total-marriages.png)

This situation is what social scientists (and economists) call a "natural experiment." The government increased the incentive to get married, and we can easily see the result.

For the three years, from 2006-2009, the government offered cash to get married. In 2006 there were more than three times the marriages of 2005. For three consecutive years, more than 30,000 marriages were registered per year. No other year on record recorded so many marriages.

Economists are probably more interested in how the new incentive changed individuals' decisions to get married. Social scientists might want to know how the institution of marriage changed, the impact on births, etc.

We can also break these marriages down by age group to see who decided to tie the knot.

![](/images/marriage-spike/marriages-by-age-group.png)

Those 20-29 took the government money at the highest rate, with the 30-39 age group following them. If we look at growth rate, both age groups more than doubled their marriage rates. Notably, the 18-19 year-old group didn't move much.

This government program has even spawned movie plot points in the Mongolian movie industry. The movie "Хуримын сюрприз" (Marriage Surprise) from 2015 is about a man wishing to marry the woman he loves, only to remember that he married his friend in college for the money. If you want to watch the trailer check it out [here](https://www.youtube.com/watch?v=Y0btMIbgZYk). It's unclear if this is based on a true story (I'm joking obviously).

## Take the Money and Run

As a socially minded data scientist, I'm more interested in how this large increase in marriages may impacted divorce. I immediately thought that a few years later divorces would spike while the people in it for the money decided to get out of their fake marriages.

Let's take a look at the time series of divorces from 1988-2020.

![](/images/marriage-spike/total-divorces.png)

This looks pretty terrible right? Beginning in 2005 divorces increased steadily. This chart alone probably reinforces the belief of many that a steady rise in divorces has been a negative symptom in society for the past decade. After all, a rise in divorces might mean more children growing up [without two parents](https://www.bbc.com/news/education-47057787), more single men who are more likely to [commit crimes](https://www.fatherly.com/health-science/are-fathers-less-likely-to-commit-crimes-biological/), and a general erosion of a cornerstone of society.

As usual though, let's dig deeper to figure out what is driving this trend. Luckily the [National Statistics Office](https://1212.mn) breaks down divorce by duration of marriage. Let's take a look.

![](/images/marriage-spike/divorces-by-duration.png)

The main trend driving the increasing numbers of divorces seems to be marriages lasting longer than 10 years. Across all marriage duration categories divorces went down in 2020. Whether due to the pandemic or another issue isn't clear.

Also notable are the smaller spikes we see for shorter duration marriages. I started getting suspicious seeing these spikes. They seemed to be staggered by duration. The 1-3 year duration divorces spike first, then the 4-6 year duration, and finally the 7-9 year duration. Coincidence? I think not.

To make things clear I highlighted the portions of each line where marriages would have happened from 2006-2009. This way we can see if divorces might have spiked because of the cash giveaway or some other trend.

![](/images/marriage-spike/divorces-duration-highlighted.png)

It's pretty astonishing how clear these spikes are. I find it nearly impossible to find another explanation for these divorce spikes. Clearly, this government program was responsible for a good portion, if not most, of the increase in divorces in the past 2 decades. Unfortunately, we don't have data on the reason for divorce. Although I doubt any survey would include "we got married for the money" as the cause of divorce.

To extend this line of thinking further, we can relatively clearly see how divorces would not be nearly as high without these spikes. It's reasonable to assume that annual divorces might be between 2,500 to 3,000 instead of more than 4,000 (a 25-35% decrease). Luckily divorces appear to be normalizing to the trend seen before the spikes.

## Conclusion

As experiments go, the results are clear. If you pay people to get married, they will. Only years later they may get divorced, causing mayhem for statistics and making your grandparents believe that society isn't what it used to be.

Each year there are between 10,000 to 20,000 marriages, and more recently, roughly 3,000 to 4,000 divorces. In the next few years, I expect that divorces will level out or even fall.

Whether this program was a mistake isn't clear. The government intended to support marriage with this initiative. This seems to be a lesson to be careful what you wish for.

> If you are interested in seeing the code used to collect or analyze the data for this article, you can find it [here](https://deepnote.com/project/Mongolias-Marriage-Spike-gOC28BVLSSyLCqzXDgpd-Q/%2FMarriage%20Spike.ipynb). 

***
#### MDS Newsletter
Thank you for reading. Mongolian Data Stories has a free newsletter! To receive new articles straight to your inbox so you never miss out, [click here to sign up](https://www.getrevue.co/profile/mongoliandatastories). 