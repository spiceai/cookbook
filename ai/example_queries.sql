-- AI SQL Function Example Queries
-- Copy and paste these into the Spice SQL REPL (spice sql)

-- ==============================================
-- BASIC-- 18. Use AI in WHERE clause (expensive - use sparingly!)
-- SELECT Zone 
-- FROM taxi_zones
-- WHERE ai(concat('Is ', Zone, ' a residential area? Answer yes or no'), 'gpt-4o-mini') = 'yes'
-- LIMIT 5;

-- 19. Generate structured data
SELECT 
  'Product Analysis' as task,
  ai('List 3 features of a smartphone, separated by commas', 'gpt-4o-mini') as features;-- ==============================================

-- 1. Simple greeting
SELECT ai('Say hello!', 'gpt-4o-mini') as greeting;

-- 2. Question answering
SELECT ai('What is 2+2? Answer with just the number.', 'gpt-4o-mini') as answer;

-- 3. Text generation
SELECT ai('Write a haiku about data', 'gpt-4o-mini') as haiku;


-- ==============================================
-- WORKING WITH DATA
-- ==============================================

-- 4. Categorize taxi zones
SELECT 
  LocationID,
  Zone,
  ai(concat('Categorize this location in one word: ', Zone), 'gpt-4o-mini') as category
FROM taxi_zones
LIMIT 5;

-- 5. Generate zone descriptions
SELECT 
  Zone,
  Borough,
  ai(concat('Describe ', Zone, ' in ', Borough, ' in one sentence'), 'gpt-4o-mini') as description
FROM taxi_zones
WHERE Borough = 'Manhattan'
LIMIT 3;

-- 6. Classify boroughs
SELECT 
  DISTINCT Borough,
  ai(concat('Is ', Borough, ' in New York City? Answer yes or no.'), 'gpt-4o-mini') as in_nyc
FROM taxi_zones;


-- ==============================================
-- SENTIMENT ANALYSIS
-- ==============================================

-- 7. Analyze customer feedback
SELECT 
  id,
  feedback,
  ai('Classify as positive, negative, or neutral: ' || feedback, 'gpt-4o-mini') as sentiment
FROM customer_feedback;

-- 8. Extract key points from feedback
SELECT 
  id,
  feedback,
  ai('What is the main point in 3 words: ' || feedback, 'gpt-4o-mini') as key_point
FROM customer_feedback
WHERE id <= 3;


-- ==============================================
-- DATA TRANSFORMATION
-- ==============================================

-- 9. Convert to title case using AI
SELECT 
  Zone,
  ai(concat('Convert to proper title case: ', LOWER(Zone)), 'gpt-4o-mini') as formatted_zone
FROM taxi_zones
LIMIT 5;

-- 10. Generate abbreviations
SELECT 
  Zone,
  ai(concat('Create a 2-3 letter abbreviation for: ', Zone), 'gpt-4o-mini') as abbreviation
FROM taxi_zones
WHERE Borough = 'Queens'
LIMIT 5;

-- 11. Translate text to different languages
SELECT 
  Zone as original,
  ai(concat_ws(' ', 'Translate to Spanish:', Zone), 'gpt-4o-mini') as spanish,
  ai(concat_ws(' ', 'Translate to French:', Zone), 'gpt-4o-mini') as french,
  ai(concat_ws(' ', 'Translate to German:', Zone), 'gpt-4o-mini') as german
FROM taxi_zones
WHERE Borough = 'Manhattan'
LIMIT 5;


-- ==============================================
-- COMBINING WITH SQL FUNCTIONS
-- ==============================================

-- 12. Use LEFT to truncate long responses
SELECT 
  Zone,
  LEFT(ai(concat('Write a detailed history of ', Zone), 'gpt-4o-mini'), 50) as short_history
FROM taxi_zones
LIMIT 3;

-- 13. Use UPPER on AI output
SELECT 
  UPPER(ai('name a color', 'gpt-4o-mini')) as color;

-- 14. Conditional AI processing
SELECT 
  Zone,
  Borough,
  CASE 
    WHEN Borough = 'Manhattan' THEN ai(concat('Describe ', Zone, ' as upscale or casual'), 'gpt-4o-mini')
    ELSE 'N/A'
  END as description
FROM taxi_zones
LIMIT 5;


-- ==============================================
-- AGGREGATION AND GROUPING
-- ==============================================

-- 15. Count responses by sentiment
SELECT 
  ai('Classify as positive, negative, or neutral: ' || feedback, 'gpt-4o-mini') as sentiment,
  COUNT(*) as count
FROM customer_feedback
GROUP BY sentiment;

-- 16. Group by AI categorization
SELECT 
  ai(concat('Urban or Suburban: ', Zone), 'gpt-4o-mini') as zone_type,
  COUNT(*) as count
FROM taxi_zones
WHERE Borough = 'Queens'
LIMIT 20;


-- ==============================================
-- ADVANCED EXAMPLES
-- ==============================================

-- 17. Chain multiple AI calls (careful - can be slow!)
SELECT 
  Zone,
  ai(concat_ws(' ', 'Translate to Spanish:', Zone), 'gpt-4o-mini') as spanish_name
FROM taxi_zones
WHERE Borough = 'Bronx'
LIMIT 3;

-- 18. Use AI in WHERE clause (expensive - use sparingly!)
-- SELECT Zone 
-- FROM taxi_zones
-- WHERE ai(concat('Is ', Zone, ' a residential area? Answer yes or no'), 'gpt-4o-mini') = 'yes'
-- LIMIT 5;

-- 18. Generate structured data
SELECT 
  'Product Analysis' as task,
  ai('List 3 features of a smartphone, separated by commas', 'gpt-4o-mini') as features;


-- ==============================================
-- COMPARING MODELS (if multiple configured)
-- ==============================================

-- 20. Compare different model responses
-- SELECT 
--   ai('What is AI?', 'gpt-4o-mini') as openai_response,
--   ai('What is AI?', 'claude-sonnet') as claude_response;


-- ==============================================
-- CHECKING TASK HISTORY
-- ==============================================

-- 21. View recent AI tasks
SELECT 
  task_id,
  task,
  execution_time,
  left(captured_output, 50) as output_preview
FROM runtime.task_history
WHERE task = 'ai'
ORDER BY captured_at DESC
LIMIT 10;
