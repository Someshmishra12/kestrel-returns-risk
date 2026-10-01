**To:** Ritu Deshpande  **Re:** Returns — what to do next week

**The decision.** Do not hold orders. Call the risky ones before dispatch instead.

**The number.** 95% accuracy can't be reached, and it isn't the right bar. About 89 in 100 orders aren't returned, so a model that does nothing is already "89% accurate". The best we can build from what is known at dispatch is about 89–90% accurate, and flagging about a fifth of all orders catches roughly 55 in 100 returns. Of the orders we flag, about 3 in 10 really come back; about 4 in 10 returns still slip through. (An earlier version scored 99% because it peeked at the reverse-pickup booking, which only exists after the customer has already returned the item. We removed it.)

**The rupees.** A return costs Rs 1,150 (finance's figure, not 600). In the latest quarter (2,096 orders) we expect about 219 returns, about Rs 2.5 lakh. Holding is a loss: 12% of held customers cancel, and we lose those sales; it loses money in our back-test. A Rs 45 call to the top ~20% of orders (about 409 calls, Rs 18,000) should stop roughly 41 returns, saving about Rs 47,000: net about Rs 29,000 a quarter, around Rs 14,000 per 1,000 orders. That depends on the spring pilot's 35% success rate holding; it still pays down to about 14%. The Rs 29,000 is the honest size of the prize; it is not a fix for the margin problem.

**Next week.**
1. Tell the board the target is rupees saved, not accuracy.
2. Run the call on orders scored above 15%, for 4 weeks, with a random fifth left uncalled to measure the real saving.
3. Never hold Shield customers; call them politely at most. They return twice as often but buy the most.
4. Ask Tanmay to fix the October payment values, the duplicate partner orders and the post-return fields in the export.
5. Ask Finance for the margin per order so we can price a hold properly.
