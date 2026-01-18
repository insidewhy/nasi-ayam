# Suggested Test Prompts

This document contains prompts designed to test various aspects of the knowledge retrieval chatbot system.

## Simple Retrieval Queries

These test basic semantic search and retrieval.

1. What are the characteristics of Maine Coon cats?
2. How do I care for orchids?
3. Tell me about Labrador Retrievers
4. What flowers attract butterflies?
5. How long do hamsters live?

## Semantic Chunking Tests

These prompts target content that tests the semantic chunking at different heading levels.

### Level 1 Heading Chunks (Small Sections)

6. What do guinea pigs sound like when they're happy?
7. How do I make a daisy chain?
8. What colors do tulips come in?

### Level 2 Heading Chunks (Large Documents)

9. What are the grooming requirements for Maine Coon cats? (tests retrieval from a subsection)
10. Tell me about the history of cottage gardens (tests retrieval from design principles section)
11. What health issues are common in Labrador Retrievers?

### Text File Paragraph Chunks

12. Why do dogs give us puppy dog eyes?
13. How do goldfish memories actually work?
14. What is a bunny binky?

### Large Text Chunks (No Parent Semantic Chunk)

15. Explain the importance of puppy socialization (from the comprehensive puppy guide)
16. What are the principles of flower garden design? (from the large garden text)

## Metadata Filtering Queries

These test filtering by source or document type.

17. What does the local documentation say about cats? (source filter)
18. Find information about dogs from PDF documents only (type filter)
19. What's in the GitHub repository about flowers?
20. List all the cat breeds mentioned in the local files

## Multi-Step Agentic Queries

These require the agent to retrieve multiple pieces of information and synthesize them.

21. Compare the personalities of Persian cats and British Shorthairs
22. Which pet would be better for someone who works from home - a rabbit or a guinea pig? Consider their social needs and care requirements.
23. I want to create a garden that attracts both butterflies and hummingbirds. What plants should I include?
24. What are the similarities and differences between Ragdoll cats and Maine Coon cats?
25. I'm considering getting either a Beagle or a Labrador Retriever. Compare their exercise needs and temperament.

## Follow-up Conversation Prompts

These test multi-turn conversation handling. Use the initial prompt, then the follow-ups.

### Conversation 1: Cat Selection

26. Initial: I'm looking for a calm, affectionate cat breed. What would you recommend?
    - Follow-up 1: What about grooming requirements for that breed?
    - Follow-up 2: Are they good with children?
    - Follow-up 3: What health issues should I watch for?

### Conversation 2: Garden Planning

27. Initial: I want to start a cottage garden. Where do I begin?
    - Follow-up 1: What flowers would work well in partial shade?
    - Follow-up 2: How do I maintain it throughout the year?
    - Follow-up 3: Can I include some plants that attract pollinators?

### Conversation 3: Puppy Training

28. Initial: I just got a new puppy. What's the most important thing I should focus on?
    - Follow-up 1: How do I socialize them properly?
    - Follow-up 2: What about potty training?
    - Follow-up 3: When should I start teaching commands?

### Conversation 4: Small Pet Research

29. Initial: What small pets are good for apartments?
    - Follow-up 1: Tell me more about hamsters
    - Follow-up 2: What about guinea pigs?
    - Follow-up 3: Which one is more cuddly?

## Confidence/Re-retrieval Triggers

These prompts might trigger the agent to search with different keywords.

30. What's the best pet for someone who wants something fluffy and cuddly?
31. I want flowers that bloom in early spring before everything else
32. Which dog breeds are known for being extremely intelligent?
33. What animals communicate through body language rather than sounds?

## Cross-Document Synthesis

These require combining information from multiple sources.

34. Create a care schedule for someone who has both a cat and a garden - what daily and weekly tasks would they need to do?
35. What are the common themes in caring for small pets like hamsters, guinea pigs, and rabbits?
36. Summarize all the information about flower colors and what affects them
37. Which pets mentioned in the documents are described as 'gentle' or have gentle temperaments?

## Edge Cases

38. What do you know about elephants? (not in documents - should indicate no relevant info)
39. Cats (very short query - should still retrieve relevant cat documents)
40. Tell me everything about the Norwegian Forest Cat from the PDF documents specifically

## Source Citation Tests

These prompts should return answers with clear source citations.

41. According to the documents, how many hours do puppies sleep?
42. What do the sources say about butterfly migration?
43. Quote the description of how Maine Coons communicate

## Complex Reasoning Queries

44. If I have limited time for pet care but want a affectionate companion, analyze which documented pets would be most suitable and why
45. Based on the gardening documents, design a year-round blooming garden plan
46. Evaluate which cat breed would be best for a family with young children based on the available information

## Topic Exploration

These are open-ended queries that should retrieve diverse relevant content.

47. What makes certain animals good pets?
48. How do different flowers attract different pollinators?
49. What are some interesting facts about animal behavior mentioned in the documents?
50. Describe the relationship between gardens and wildlife based on the documentation
