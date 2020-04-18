🏎 Hyper Shopping 🏎
------------------

Race through your shopping list!

What is HyperShop
~~~~~~~~~~~~~~~~~

At the root of HyperShop is a shopping list hypernim extractor for matching item category to supermarket section.

It takes in a shopping list (e.g manually enterred, or from a TODO app like Trello), categorizes the items (with user prompts in case of unclear items), and
re-orders the list to group the categories together. The categories themselves are ordered according a given supermarket layout and the path you choose to take.

Flow
~~~~

1. Download shopping card from Trello in JSON format
2. Parse the card JSON and retreive checklist items
3. Iterate over all items, and fetch hypernims for all synonymous words
4. Provide prompts to user if unmpet category to:

   - offer to fix typos using e.g the gensim package
   - display category for the (corrected) item
   - optioanlly select another category
   - optionally enter custom/new category

5. Select supermarket and display the route through departments
