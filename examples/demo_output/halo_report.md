# Studio Quattro Design - Halo Strategy Research Brief

_Generated 2026-10-10T06:45:43+00:00 - 50 posts across google (14), yelp (11), reddit (25)._

> **Note:** this run used the bundled **synthetic fixture dataset** (illustrative, not real customers). Run `mine` or `import` against live sources for production numbers.

Framework: Sabri Suby's Halo Strategy - mine where the dream buyer already talks, capture their exact words, sort into **Pains, Fears, Hopes, Dreams, Testimonials**, and weight toward **3-4★ reviews** and the **longest posts**.

## 1. Numbers at a glance

| Metric | Value |
|---|---|
| Posts analysed | 50 |
| Total words | 3055 |
| Avg / median words per post | 61.1 / 54.5 |
| Long-post threshold (p75) | 79.8 words (13 posts) |
| Rated reviews | 25 |
| Average rating | 3.40 |
| 3-4★ share of rated reviews | 52.0% |
| Emotional intensity (intensifiers / 100 words) | 0.91 |
| First-person density (/100 words) | 6.72 |

### Star distribution

| Stars | Reviews | Share |  | Avg words |
|---|---|---|---|---|
| 5★ | 6 | 24.0% | █████░░░░░░░░░░░░░░░ | 30.3 |
| 4★ | 7 | 28.0% | ██████░░░░░░░░░░░░░░ | 71.9 |
| 3★ | 6 | 24.0% | █████░░░░░░░░░░░░░░░ | 87.3 |
| 2★ | 3 | 12.0% | ██░░░░░░░░░░░░░░░░░░ | 54.0 |
| 1★ | 3 | 12.0% | ██░░░░░░░░░░░░░░░░░░ | 22.7 |

### Why the middle matters

| Band | Complaint signal | Praise signal | Complaint:praise | Both present | Avg words |
|---|---|---|---|---|---|
| 5-star | 5.50 | 45.5 | 0.12 | 33.3% | 30.3 |
| 3-4 star | 56.5 | 46.0 | 1.23 | 76.9% | 79.0 |
| 1-2 star | 46.5 | 0.00 | ∞ | 0.0% | 38.3 |
| unrated | 117.5 | 17.0 | 6.91 | 12.0% | 64.6 |

_3-4★ reviews carry both praise and complaint in the same post far more often - that is the "what I wanted vs what I got" gap the Halo Strategy mines for._

## 2. The five Halo buckets

| Bucket | Posts w/ signal | % | Primary | Hits/1k words | Halo-weighted share |  |
|---|---|---|---|---|---|---|
| Pains & frustrations | 32 | 64.0% | 14 | 45.2 | 27.9% | ██████░░░░░░░░░░░░░░ |
| Fears & anxieties | 24 | 48.0% | 10 | 28.8 | 20.5% | ████░░░░░░░░░░░░░░░░ |
| Hopes | 22 | 44.0% | 6 | 21.9 | 15.6% | ███░░░░░░░░░░░░░░░░░ |
| Dreams | 27 | 54.0% | 8 | 28.0 | 17.3% | ███░░░░░░░░░░░░░░░░░ |
| Testimonials & proof language | 22 | 44.0% | 10 | 35.5 | 18.7% | ████░░░░░░░░░░░░░░░░ |

### Density by star band (mean hits per 100 words)

| Bucket | 1-2 star (n=6) | 3-4 star (n=13) | 5-star (n=6) | unrated (n=25) |
|---|---|---|---|---|
| Pains & frustrations | 24.4 | 4.10 | 2.00 | 2.97 |
| Fears & anxieties | 4.01 | 2.14 | 0.00 | 3.53 |
| Hopes | 1.85 | 2.58 | 0.86 | 1.28 |
| Dreams | 1.52 | 2.55 | 15.2 | 1.69 |
| Testimonials & proof language | 0.00 | 4.89 | 30.2 | 0.74 |

## 3. What they talk about (topics)

| Topic | Sentence hits | Posts mentioning | Dominant bucket |
|---|---|---|---|
| budget & pricing | 64 | 68.0% | pains |
| designer value & fit | 36 | 54.0% | fears |
| function & livability | 29 | 50.0% | pains |
| timeline & delays | 26 | 36.0% | pains |
| style, taste & cohesion | 23 | 30.0% | pains |
| process & decision stress | 22 | 34.0% | pains |
| communication & responsiveness | 19 | 34.0% | pains |
| trust & honesty | 16 | 28.0% | hopes |
| contractors & trades | 14 | 22.0% | pains |
| quality & craftsmanship | 6 | 10.0% | pains |

## 4. Correlations (Pearson r)

| Pair | r |
|---|---|
| Post length ↔ total emotional signal | 0.60 |
| Post length ↔ pain density | -0.21 |
| Post length ↔ dream density | -0.18 |
| Star rating ↔ pain score | -0.75 |
| Star rating ↔ testimonial score | 0.69 |

_Positive length↔signal confirms the Halo rule: longer posts are richer. Strongly negative rating↔pain means low stars are mostly venting; look to 3-4★ for balanced detail._

## 5. Swipe file - their exact words

Ranked by quote strength x Halo weight (3-4★ and long posts float up). Use verbatim where possible; the market's language beats the copywriter's.

### Pains & frustrations (what hurts right now)

Most-used phrases: **expensive** (4), **overwhelmed** (3), **over budget** (3), **stressful** (2), **showroom** (2), **mess** (2), **markups** (2), **regret** (2), **exhausted** (2), **dated** (2)

- “I'm scared of two things: that we spend the money and end up with a house that looks like a hotel lobby and not like us, and that we DON'T spend it and end up with a piecemeal mess we hate for twenty years.”  
  <sub>reddit, 136 words, halo 3.67 - https://www.reddit.com/r/homeowners/comments/x1/</sub>
- “I want to keep some of the pieces that matter but the house is dark, dated and cluttered and I need it to feel like a fresh start for my own kids.”  
  <sub>reddit, 81 words, halo 2.98 - https://www.reddit.com/r/homeowners/comments/x10/</sub>
- “We went slightly over budget (about 10%) but she told us where every dollar went.”  
  <sub>reddit, 173 words, halo 4.03 - https://www.reddit.com/r/kitchenremodel/comments/x3/</sub>
- “Overwhelmed and paralysed by choices - how do people decide?”  
  <sub>reddit, 71 words, halo 2.97 - https://www.reddit.com/r/HomeDecorating/comments/x5/</sub>
- “The decision paralysis was costing me more in stress than the fee.”  
  <sub>reddit, 60 words, halo 2.62 - https://www.reddit.com/r/HomeDecorating/comments/x5/c1</sub>
- “We went 30% over budget, mostly on 'while the walls are open' decisions.”  
  <sub>reddit, 108 words, halo 3.49 - https://www.reddit.com/r/Renovations/comments/x2/</sub>
- “The one thing I'd change: the furniture markups were higher than I expected and weren't super transparent until we asked.”  
  <sub>yelp, 4★, 93 words, halo 2.71</sub>
- “But the invoices were confusing, there were markups we didn't know about on furniture, and when I questioned them it got defensive.”  
  <sub>yelp, 3★, 77 words, halo 2.52</sub>
- “Honestly the best part was having someone make the decisions with us - I was so overwhelmed by tile options I had basically stopped sleeping.”  
  <sub>google, 4★, 94 words, halo 2.71</sub>
- “Two stars because the final look is okay, but it was a nightmare getting here and I was exhausted by the end.”  
  <sub>google, 2★, 49 words, halo 1.65</sub>
- “Also ask who manages the contractors, because we assumed she did and she assumed we did and that was a very stressful month.”  
  <sub>reddit, 118 words, halo 3.37 - https://www.reddit.com/r/homeowners/comments/x1/c1</sub>
- “We paid a large deposit, got three mood boards that looked like generic Pinterest, and then they became unresponsive.”  
  <sub>yelp, 1★, 32 words, halo 1.42</sub>

### Fears & anxieties (what they are afraid will happen)

Most-used phrases: **upfront** (4), **no idea** (3), **worth it** (3), **deposit** (2), **anxious** (2), **afford** (2), **mistake** (2), **trusting** (2), **nervous** (2), **afraid** (2)

- “I'm scared of two things: that we spend the money and end up with a house that looks like a hotel lobby and not like us, and that we DON'T spend it and end up with a piecemeal mess we hate for twenty years.”  
  <sub>reddit, 136 words, halo 3.67 - https://www.reddit.com/r/homeowners/comments/x1/</sub>
- “I think I'm afraid of making an expensive permanent mistake and then having to live with it and look at it every day.”  
  <sub>reddit, 71 words, halo 2.97 - https://www.reddit.com/r/HomeDecorating/comments/x5/</sub>
- “My fear was that they'd impose their taste on us and we'd end up living in someone else's house, or that it would cost a fortune and I'd be too embarrassed to say stop.”  
  <sub>yelp, 4★, 93 words, halo 2.71</sub>
- “Got a quote for $150/hr plus a 20% markup on furniture and I have no idea if that's normal or a rip-off.”  
  <sub>reddit, 72 words, halo 2.65 - https://www.reddit.com/r/InteriorDesign/comments/x4/</sub>
- “The full service was worth it - no surprises, kept us in the loop weekly, and they saved us from a very expensive mistake with a kitchen island that would have blocked the dishwasher.”  
  <sub>yelp, 4★, 97 words, halo 2.85</sub>
- “The design was worth every penny - we would never have had the vision for the open kitchen and she saved us from at least two expensive mistakes with the layout.”  
  <sub>reddit, 118 words, halo 3.37 - https://www.reddit.com/r/homeowners/comments/x1/c1</sub>
- “Started with an e-design service - cheap, but the renderings didn't account for our actual plumbing and we couldn't afford to move it.”  
  <sub>reddit, 173 words, halo 4.03 - https://www.reddit.com/r/kitchenremodel/comments/x3/</sub>
- “Budget is reasonable but not unlimited and we're nervous about getting talked into something that doesn't feel like us.”  
  <sub>reddit, 95 words, halo 2.97 - https://www.reddit.com/r/InteriorDesign/comments/x7/</sub>
- “My only gripe is the hourly billing - it made me anxious to send emails because every question felt like it cost money.”  
  <sub>google, 4★, 70 words, halo 2.57</sub>
- “I have no idea how to do that without feeling like I'm erasing him.”  
  <sub>reddit, 81 words, halo 2.98 - https://www.reddit.com/r/homeowners/comments/x10/</sub>
- “The designer herself was lovely and patient with my endless second-guessing.”  
  <sub>yelp, 3★, 135 words, halo 3.02</sub>
- “Communication went quiet for two weeks in the middle and we had no idea whether the sofa had even been ordered.”  
  <sub>google, 3★, 86 words, halo 2.69</sub>

### Hopes (what they are actively seeking)

Most-used phrases: **finally** (7), **cohesive** (4), **wish** (4), **storage** (4), **want to** (4), **trying to** (2), **hoped** (2), **age well** (1), **someone to** (1), **wanted to** (1)

- “What we hoped for: a cohesive home that felt grown-up after a decade of hand-me-down furniture, something that would age well and not look dated in five years.”  
  <sub>yelp, 3★, 135 words, halo 3.02</sub>
- “Finally hired a local designer and I wish we'd started there.”  
  <sub>reddit, 173 words, halo 4.03 - https://www.reddit.com/r/kitchenremodel/comments/x3/</sub>
- “We'd love something calm and a bit elegant - a place that feels like a retreat where we actually want to host our friends.”  
  <sub>reddit, 95 words, halo 2.97 - https://www.reddit.com/r/InteriorDesign/comments/x7/</sub>
- “Pros: she pulled together a house we'd been fighting over for three years, found storage we didn't know we had, and the colour palette finally flows from room to room.”  
  <sub>google, 3★, 132 words, halo 2.94</sub>
- “The design itself is genuinely beautiful - our living room finally feels cohesive and guests always comment on it.”  
  <sub>google, 3★, 86 words, halo 2.69</sub>
- “My fault for not pushing back harder, but I was hoping for more guidance than 'what do you like on Pinterest'.”  
  <sub>yelp, 2★, 47 words, halo 1.65</sub>
- “We're empty nesters who finally wanted the house to feel like a retreat instead of a kid storage unit.”  
  <sub>google, 4★, 70 words, halo 2.57</sub>
- “The e-design was good but we quickly realised we needed someone to actually coordinate the contractors, so we upgraded.”  
  <sub>yelp, 4★, 97 words, halo 2.85</sub>
- “What did you wish you'd known about fees?”  
  <sub>reddit, 136 words, halo 3.67 - https://www.reddit.com/r/homeowners/comments/x1/</sub>
- “Four stars not five because the timeline slipped by about six weeks when the cabinet maker fell behind, and I wish they had warned us earlier.”  
  <sub>google, 4★, 94 words, halo 2.71</sub>
- “Spa-like, exactly what we hoped for, and the tile work is meticulous.”  
  <sub>google, 4★, 53 words, halo 2.31</sub>
- “Are there designers who do that or is 'cohesive' just code for 'bland'?”  
  <sub>reddit, 55 words, halo 2.86 - https://www.reddit.com/r/InteriorDesign/comments/x9/</sub>

### Dreams (the vivid after-picture they long for)

Most-used phrases: **beautiful** (3), **feel like a** (3), **calm** (3), **feels like** (3), **feels like a** (3), **vision** (2), **retreat** (2), **forever home** (2), **personality** (2), **light-filled** (1)

- “We'd love something calm and a bit elegant - a place that feels like a retreat where we actually want to host our friends.”  
  <sub>reddit, 95 words, halo 2.97 - https://www.reddit.com/r/InteriorDesign/comments/x7/</sub>
- “The finished house is genuinely beautiful and I'm proud of it, but I was so exhausted by the end I couldn't enjoy it for weeks.”  
  <sub>reddit, 108 words, halo 3.49 - https://www.reddit.com/r/Renovations/comments/x2/</sub>
- “She has a wonderful eye and really listened to what we wanted, which was a calm, light-filled space that didn't feel like a showroom.”  
  <sub>yelp, 3★, 80 words, halo 2.64</sub>
- “Finally finished our forever home kitchen after 2 years - what I learned.”  
  <sub>reddit, 173 words, halo 4.03 - https://www.reddit.com/r/kitchenremodel/comments/x3/</sub>
- “We're empty nesters who finally wanted the house to feel like a retreat instead of a kid storage unit.”  
  <sub>google, 4★, 70 words, halo 2.57</sub>
- “I want a home with personality, colour, our books, our weird stuff.”  
  <sub>reddit, 55 words, halo 2.86 - https://www.reddit.com/r/InteriorDesign/comments/x9/</sub>
- “I think I'm afraid of making an expensive permanent mistake and then having to live with it and look at it every day.”  
  <sub>reddit, 71 words, halo 2.97 - https://www.reddit.com/r/HomeDecorating/comments/x5/</sub>
- “The house looks beautiful - warm, inviting, not at all sterile - and the storage solutions are genius.”  
  <sub>google, 4★, 59 words, halo 2.55</sub>
- “The design was worth every penny - we would never have had the vision for the open kitchen and she saved us from at least two expensive mistakes with the layout.”  
  <sub>reddit, 118 words, halo 3.37 - https://www.reddit.com/r/homeowners/comments/x1/c1</sub>
- “I want to keep some of the pieces that matter but the house is dark, dated and cluttered and I need it to feel like a fresh start for my own kids.”  
  <sub>reddit, 81 words, halo 2.98 - https://www.reddit.com/r/homeowners/comments/x10/</sub>
- “They listened, they were patient with us changing our minds, and they turned a dark cramped 1970s ranch into a bright, open home that feels like a resort.”  
  <sub>google, 5★, 38 words, halo 1.17</sub>
- “Spa-like, exactly what we hoped for, and the tile work is meticulous.”  
  <sub>google, 4★, 53 words, halo 2.31</sub>

### Testimonials & proof language (how delight sounds)

Most-used phrases: **communication** (3), **professional** (3), **honest** (3), **listened** (2), **transparent** (2), **worth every penny** (2), **patient** (2), **saved us from** (2), **recommend** (1), **incredible** (1)

- “The design was worth every penny - we would never have had the vision for the open kitchen and she saved us from at least two expensive mistakes with the layout.”  
  <sub>reddit, 118 words, halo 3.37 - https://www.reddit.com/r/homeowners/comments/x1/c1</sub>
- “The full service was worth it - no surprises, kept us in the loop weekly, and they saved us from a very expensive mistake with a kitchen island that would have blocked the dishwasher.”  
  <sub>yelp, 4★, 97 words, halo 2.85</sub>
- “Attention to detail was great, the install day was seamless.”  
  <sub>google, 4★, 70 words, halo 2.57</sub>
- “Lessons: decide who's managing trades, fix the budget before you fall in love with anything, and hire for how they listen not for their Instagram.”  
  <sub>reddit, 173 words, halo 4.03 - https://www.reddit.com/r/kitchenremodel/comments/x3/</sub>
- “The one thing I'd change: the furniture markups were higher than I expected and weren't super transparent until we asked.”  
  <sub>yelp, 4★, 93 words, halo 2.71</sub>
- “Best money I spent on the whole house.”  
  <sub>reddit, 60 words, halo 2.62 - https://www.reddit.com/r/HomeDecorating/comments/x5/c1</sub>
- “I don't think anyone was dishonest, I think they just aren't transparent by default, and for this amount of money I needed to feel I could trust the numbers.”  
  <sub>yelp, 3★, 77 words, halo 2.52</sub>
- “Professional, responsive, on time and on budget.”  
  <sub>google, 5★, 26 words, halo 1.09</sub>
- “She has a wonderful eye and really listened to what we wanted, which was a calm, light-filled space that didn't feel like a showroom.”  
  <sub>yelp, 3★, 80 words, halo 2.64</sub>
- “Here is my honest take after a full-home project that took eleven months.”  
  <sub>yelp, 3★, 135 words, halo 3.02</sub>
- “They listened, they were patient with us changing our minds, and they turned a dark cramped 1970s ranch into a bright, open home that feels like a resort.”  
  <sub>google, 5★, 38 words, halo 1.17</sub>
- “Would hire again, with a buffer in the schedule.”  
  <sub>google, 4★, 59 words, halo 2.55</sub>

## 6. What they've tried & what triggers the search

**Objections / alternatives already considered:** worth it (4), pinterest (3), hourly (3), instagram (3), estimate (2), e-design (2), quoted (2), diy (2), flat fee (2), do it ourselves (1), consultation (1), percentage (1), save money (1), markup (1)

**Buying triggers (life events):** renovation (4), kids (3), kid (2), empty nesters (2), remodel (1), toddlers (1), just bought (1), expecting (1), renovating (1), holidays (1), teenagers (1), just closed (1), in-laws (1), addition (1), working from home (1)

## 7. Priority reading lists

### 3-4★ reviews (balanced, most honest) - top by Halo score

- **3★ · 135 words · halo 3.02 · hopes** - “What we hoped for: a cohesive home that felt grown-up after a decade of hand-me-down furniture, something that would age well and not look dated in five years.”
- **3★ · 132 words · halo 2.94 · hopes** - “Pros: she pulled together a house we'd been fighting over for three years, found storage we didn't know we had, and the colour palette finally flows from room to room.”
- **4★ · 97 words · halo 2.85 · testimonials** - “The full service was worth it - no surprises, kept us in the loop weekly, and they saved us from a very expensive mistake with a kitchen island that would have blocked the dishwasher.”
- **4★ · 94 words · halo 2.71 · hopes** - “Four stars not five because the timeline slipped by about six weeks when the cabinet maker fell behind, and I wish they had warned us earlier.”
- **4★ · 93 words · halo 2.71 · fears** - “My fear was that they'd impose their taste on us and we'd end up living in someone else's house, or that it would cost a fortune and I'd be too embarrassed to say stop.”
- **3★ · 86 words · halo 2.69 · pains** - “The final invoice was about 15% over the estimate because of change orders we didn't fully understand.”
- **3★ · 80 words · halo 2.64 · dreams** - “She has a wonderful eye and really listened to what we wanted, which was a calm, light-filled space that didn't feel like a showroom.”
- **4★ · 70 words · halo 2.57 · dreams** - “We're empty nesters who finally wanted the house to feel like a retreat instead of a kid storage unit.”
- **4★ · 59 words · halo 2.55 · testimonials** - “Would hire again, with a buffer in the schedule.”
- **3★ · 77 words · halo 2.52 · testimonials** - “I don't think anyone was dishonest, I think they just aren't transparent by default, and for this amount of money I needed to feel I could trust the numbers.”

### Longest posts (most invested voices)

- **173 words · reddit · dreams** - “Finally finished our forever home kitchen after 2 years - what I learned.” - https://www.reddit.com/r/kitchenremodel/comments/x3/
- **136 words · reddit · fears** - “I'm scared of two things: that we spend the money and end up with a house that looks like a hotel lobby and not like us, and that we DON'T spend it and end up with a piecemeal mess we hate for twenty years.” - https://www.reddit.com/r/homeowners/comments/x1/
- **3★ · 135 words · yelp · hopes** - “What we hoped for: a cohesive home that felt grown-up after a decade of hand-me-down furniture, something that would age well and not look dated in five years.”
- **3★ · 132 words · google · hopes** - “Pros: she pulled together a house we'd been fighting over for three years, found storage we didn't know we had, and the colour palette finally flows from room to room.”
- **118 words · reddit · fears** - “The design was worth every penny - we would never have had the vision for the open kitchen and she saved us from at least two expensive mistakes with the layout.” - https://www.reddit.com/r/homeowners/comments/x1/c1
- **108 words · reddit · pains** - “We went 30% over budget, mostly on 'while the walls are open' decisions.” - https://www.reddit.com/r/Renovations/comments/x2/
- **4★ · 97 words · yelp · testimonials** - “The full service was worth it - no surprises, kept us in the loop weekly, and they saved us from a very expensive mistake with a kitchen island that would have blocked the dishwasher.”
- **95 words · reddit · dreams** - “We'd love something calm and a bit elegant - a place that feels like a retreat where we actually want to host our friends.” - https://www.reddit.com/r/InteriorDesign/comments/x7/
- **4★ · 94 words · google · hopes** - “Four stars not five because the timeline slipped by about six weeks when the cabinet maker fell behind, and I wish they had warned us earlier.”
- **4★ · 93 words · yelp · fears** - “My fear was that they'd impose their taste on us and we'd end up living in someone else's house, or that it would cost a fortune and I'd be too embarrassed to say stop.”

### Highest Halo score overall

- **halo 4.03 · 173 words · reddit** - “Finally finished our forever home kitchen after 2 years - what I learned.”
- **halo 3.67 · 136 words · reddit** - “I'm scared of two things: that we spend the money and end up with a house that looks like a hotel lobby and not like us, and that we DON'T spend it and end up with a piecemeal mess we hate for twenty years.”
- **halo 3.49 · 108 words · reddit** - “We went 30% over budget, mostly on 'while the walls are open' decisions.”
- **halo 3.37 · 118 words · reddit** - “The design was worth every penny - we would never have had the vision for the open kitchen and she saved us from at least two expensive mistakes with the layout.”
- **halo 3.02 · 3★ · 135 words · yelp** - “What we hoped for: a cohesive home that felt grown-up after a decade of hand-me-down furniture, something that would age well and not look dated in five years.”
- **halo 2.98 · 81 words · reddit** - “I want to keep some of the pieces that matter but the house is dark, dated and cluttered and I need it to feel like a fresh start for my own kids.”
- **halo 2.97 · 71 words · reddit** - “I think I'm afraid of making an expensive permanent mistake and then having to live with it and look at it every day.”
- **halo 2.97 · 95 words · reddit** - “We'd love something calm and a bit elegant - a place that feels like a retreat where we actually want to host our friends.”
- **halo 2.94 · 3★ · 132 words · google** - “Pros: she pulled together a house we'd been fighting over for three years, found storage we didn't know we had, and the colour palette finally flows from room to room.”
- **halo 2.86 · 55 words · reddit** - “I want a home with personality, colour, our books, our weird stuff.”

## 8. Keyword & phrase frequency (from quotable sentences)

- **pains:** house looks (2) · furniture (5), budget (4), something (4), home (4), house (4), didn't (3), decisions (3), feel (3)
- **fears:** money (4), idea (3), house (3), every (3), expensive (3), upfront (3), feel (3), i'm (3)
- **hopes:** finally feels (2), home finally (2) · finally (6), house (4), storage (4), feels (3), cohesive (3), wish (3), home (3), we'd (3)
- **dreams:** house feels (3), finally feels (2), genuinely beautiful (2), home finally (2), feels ours (2), forever home (2) · feels (7), home (7), house (7), finally (5), feel (4), beautiful (3), kitchen (3), room (2)
- **testimonials:** budget (3), kitchen (3), home (3), communication (2), whether (2), feel (2), space (2), listened (2)

## 9. Copy angles for the copywriter

- **Lead with the #1 topic (budget & pricing).** Open the page on what they talk about most (68.0% of posts), not on the portfolio.
- **Pain hook:** "Interior design without budget surprises, rooms that photograph well but don't work or the timeline that quietly doubles."
- **Promise stack:** knowing the number before you start; a home that works for how you actually live; a schedule you can plan your life around.
- **Agitate in their words:** open with the top pain line verbatim - “I want to keep some of the pieces that matter but the house is dark, dated and cluttered and I need it to feel like a fresh start for my…” - then name the gap it describes.
- **Risk reversal:** the fear to answer head-on is “I'm scared of two things: that we spend the money and end up with a house that looks like a hotel lobby and not like us, and that we DON'T…”. Counter it with a fixed-fee scope, a written schedule with milestone payments, or a guarantee.
- **Core promise:** what they are actually seeking - “What we hoped for: a cohesive home that felt grown-up after a decade of hand-me-down furniture, something that would age well and not look…”. Make this the sub-headline.
- **After-picture:** paint this in the first 10 seconds of any video or landing page - “We'd love something calm and a bit elegant - a place that feels like a retreat where we actually want to host our friends”.
- **Proof language to echo:** “communication”, “professional”, “honest”, “listened”, “transparent” - the exact words delighted clients reach for; use them as testimonial headlines and in the guarantee.
- **Pre-empt objections / alternatives tried:** worth it, pinterest, hourly, instagram - address each in an FAQ before the call-to-action.
- **Godfather offer test:** build an offer that removes the top fear and guarantees the top hope; price it against the cost of the top pain.
- **High-value content offer (HVCO) idea for Studio Quattro Design:** "The renovation mistakes 13 homeowners wish they'd avoided" - sourced from the 3-4★ reading list below.

## 10. Method notes

- **Weights:** 3★/4★ x1.5, 2★ x1.1, 1★ x0.9, 5★ x0.8, Reddit x1.0; length on a log curve (capped x3); small boosts for upvotes/comments and emotional intensity.
- **Classification:** sentence-level weighted phrase lexicon (editable in config). Add `--llm` to re-classify with Claude for nuance.
- **Caveats:** lexicon matching is a first pass; read the priority lists yourself - the Halo Strategy is about absorbing the voice, not just counting it.
