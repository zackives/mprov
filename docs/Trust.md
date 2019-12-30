# Reasoning about Trust

A key aspect of PennProv is making a connection between *provenance* and *trust*.  This is particularly relevant when 
we have (human and automated) *annotators* who add annotations over multi-modal data, such as images and time series.

We consider two aspects of this problem:

1. What are the **vote aggregation** schemes that one could employ, where each annotator has a vote and the 
gold-standard truth isn't known?

1. How do we take annotations over a time series or images, and convert them into "votes" that can be aggregated, given 
the continuous nature of the data?

We describe each below.

## Aggregating Trust

In recent years, a number of advances have been made across the crowdsourcing, statistics, and machine learning 
communities on aggregating votes into labels for training or classification.  The basic problem setup is simple:

* We have *k* **agents** who "vote" (classify, e.g., in binary form) on up to **n** items. (An agent may choose to 
only vote on a subset of the items.)  
* We seek to determine (1) the "most likely" classification of each item, (2) the *reliability* of each agent.

Of course, a simple scheme is simply to use majority voting, but of course the different agents may have different 
levels of ability.  Instead, we may wish to consider the **most likely** classifications, if we look at each agent's 
reliability vs the consensus (when scaled by each agent's reliability).

Perhaps the first notable work in this space was the Dawid-Skene algorithm based on expectation maximization (EM), 
in [[Dawid/Skene 1979]](https://rss.onlinelibrary.wiley.com/doi/abs/10.2307/2346806). 

Later researchers have worked on related schemes, such as Fast Dawid-Skene by [[Sinha, Rao, and Balasubramanian]](https://arxiv.org/abs/1803.02781).

We support all of these methods through the `pennprov.trust.trust` package:
* MajorityVoteTrust
* DawidSkeneTrust
* FastDawidSkeneTrust
* HybridDawidSkeneTrust

### Aggregating Votes / Classifications

For each of these classes, you can call `get_trust(item_set_struct)` to assess the likely classification for each item in the 
`item_set_struct`.  The structure should be set up as follows:

`{agent: {item_key: vote}}`

where `agent` is the unique ID of each agent; `item_key` is a unique ID for each item (see below for how to convert from 
time series or image data); and `vote` is a non-empty item.  By default we assume that we are doing binary classification; 
if an `item_key`/`vote` combination, is present this is treated as a positive vote, and if the `item_key` is absent this 
is treated as a negative vote.

### Assessing Trustworthiness

A second question is how trustworthy **an agent** should be considered to be.


## Converting Annotations over Multimodal Data to Votes

 