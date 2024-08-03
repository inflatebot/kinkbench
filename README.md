# Kinkbench - Make your models grade their *own* writing.

Kinkbench is a semi-supervised evaluation utility for models intended to produce fetish-oriented content. (It may however be useful to anybody developing models which require knowledge which may be very low-rank in their foundations.)

The intention is for the user to read the generated samples, then compare their findings to the model's self-report, so as to develop an understanding of the model's priorities which, ideally, are more consistent than chance.
It was originally conceived after I noticed that Helide had a tendency to veer darker than anticipated in testing, and when asking about its priorities directly, it seemed to value this aspect quite highly.

It generates, in-context, 2 short stories, then, in-context, queries the model about how well it thinks it did.
It then, out-of-context, performs a multi-shot evaluation on each sample, asking more specific questions.
Kinkbench is configured via `run_config.yaml`, with everything from the LLM parameters to the specific questions being asked being configurable this way.
Currently, it's built for KoboldCPP; however adapting it to something like LiteLLM would be pretty easy.

The default configuration is for Llama 3 models, and the generation parameters replicate KoboldCPP's "Simple Balanced" preset.
By default, generation is multi-shot, in 100-token segments (this is configurable.)

The full MSE battery looks like this (currently, 4 out of 7 are implemented:)
```
1. This sample is intended to be a snippet of fetish erotica. [explain rating tag] To that end, how well do you think the sample fares? Give a general review. Be honest, and consider the following aspects:
- Prose (how well was it written, aesthetically speaking?)
- Inclusion of elements (how well does the sample integrate its intended themes? does it serve its purpose?)
- Internal logical consistency (does anything stand out as strange, when accounting for suspension of disbelief? Are there logical errors?)
- Does the rating of <rating> fit with the content?

2. Setting aside the story itself for the moment. Given the tags for this story, "[tag-list]": What might the intended reader be like? What do you think the personality and [sexual] proclivities of this imagined reader might be? Does this story appeal to them? Why or why not?

3. Set aside the first imagined reader, and answer the previous question again for a second imagined reader. This new imagined reader should enjoy stories with the sample's tags the same as the first, but should have the opposite opinion of this story in particular; that is to say, if you believe the first *would* enjoy this story, imagine one who *doesn't*, and vice versa.

4. The intended focus of this story is [whichever-tag]. What do you think is [interesting,arousing] about this topic? Does this story do a good job of expressing this?

5. Within this story, the following issues were found by human readers.
[Issue] - [Count]
[etc...]
Can you identify where these issues are?
(TODO: Add a prompt where these can be entered.)

6. The writer of this story had the following to say: "<In-place Evaluation>" Do you agree? Why or why not? What might you suggest?
(TODO: Might need to rework the way input files are handled.)

7. Do you think this story was written by a person or a large language model? Why?
(TODO: This one could be done right now actually, but it might be better served with the other two first.)
```

Special thanks to the BeaverAI Discord server.