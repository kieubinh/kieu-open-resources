"""English edition of EP04 — same scene ids, modes, timings and traces as episode.py."""
from episode import sc

S=[
sc('01-mission','KIEU STUDIO / THE ART OF CODING','Learn how to think, not code to memorize',[
 'UNDERSTAND → HYPOTHESIZE → TEST → REFLECT',
 'LeetCode is the practice ground. Problem-solving is the goal.'],
 '''Welcome to Kieu Studio, The Art of Coding. In this series we do not treat LeetCode as a collection of answers to memorize. Every problem is a chance to practise solving problems. Today you will learn to read a requirement carefully, spot the conditions that matter, form a hypothesis, test it yourself, and only then write code. If hard problems have ever felt intimidating, try learning with us in exactly this order. The important question is not which line of code to write first, but why we need that line at all.''',49,'mission'),
sc('02-hook','01 / THE STORY','Two sorted lines — find the true middle',[
 'One blue line and one yellow line, each sorted in increasing order.',
 'We do not want to merge everything into one long line.',
 'Can we find the middle with just a few comparisons?'],
 '''Imagine two lines of people, each already standing from shortest to tallest. We want the person who would stand in the middle if both lines were combined. The natural approach is to ask everyone to merge into a single line. But if one line is extremely long, rebuilding the order from scratch is wasteful. The interesting part is that the order inside each line already carries most of the information. Why move everyone when we could find the right place to split? That is the heart of problem number four.''',46,'story'),
sc('03-problem','02 / READ THE PROBLEM','Median of Two Sorted Arrays',[
 'Input: nums1, nums2 — two arrays sorted in increasing order',
 'Output: the median of all elements',
 'Required time: O(log(m+n))'],
 '''LeetCode problem four is called Median of Two Sorted Arrays. We are given two integer arrays, nums one and nums two. Each array is already sorted in increasing order. We must return the median of all elements from both arrays, as if they formed one ordered collection. One requirement we cannot skip is the running time: big O of log of m plus n. This is not just optimization advice. It means a solution that walks through every element does not meet the problem's goal.''',46,'problem'),
sc('04-median','02 / READ THE PROBLEM','What does median mean?',[
 'Odd total: take the element exactly in the middle.',
 'Even total: average the two middle elements.',
 'The median is not the average of the whole array.'],
 '''If the number of elements is odd, the median is the single element in the middle after sorting. For one, two, three, the answer is two. If the number of elements is even, for example one, two, three, four, we take the average of two and three, which is two point five. This is where many people confuse the median with the mean. The mean averages all the values. The median is the middle position in the order. For this problem we only need one or two middle elements, not the whole merged sequence.''',46,'median'),
sc('05-constraints','02 / READ THE PROBLEM','Read every constraint',[
 '0 ≤ m ≤ 1000; 0 ≤ n ≤ 1000',
 '1 ≤ m+n ≤ 2000',
 '−10⁶ ≤ nums1[i], nums2[i] ≤ 10⁶',
 'One array may be empty; both cannot be empty.'],
 '''Look closely at the constraints, because they produce the test cases. Each array has between zero and one thousand elements, but together they have at least one and at most two thousand. That means one of the arrays can be completely empty. The integers range from minus one million to plus one million, so we will see negative numbers, zeros and duplicates. When we test a solution, we must ask ourselves: what if the left side has no elements? What if the two values at the boundary are equal? What if the total is even?''',50,'constraints'),
sc('06-stats','02 / READ THE PROBLEM','Difficulty and verified statistics',[
 'Difficulty: HARD (LeetCode)',
 'Acceptance: 46.4% (Leetbot, snapshot 4 Sep 2026)',
 'Do not infer the number of solvers from submissions.',
 'Accepted/total submissions: not verified.'],
 '''LeetCode rates this problem as Hard. The Leetbot dataset, updated on the fourth of September twenty twenty-six, records an acceptance rate of forty-six point four percent. That is a snapshot from a specific date, not a live rate at the moment you are watching. We do not have reliable numbers for accepted submissions and total submissions from the same date, so we will not make those numbers up. More importantly, submissions are attempts, not people.''',47,'stats'),
sc('07-ex1','03 / OFFICIAL EXAMPLES','Example 1 — odd total',[
 'nums1 = [1,3]   nums2 = [2]',
 'Imagine merging: [1,2,3]',
 'Output: 2.00000'],
 '''In the first example, nums one is one and three, and nums two contains just the number two. If we merge them to picture the answer, we get one, two, three. There are three elements in total, so the median is two, and the output is two point zero zero zero zero zero. On screen, notice the two standing between both sides. But remember: we merge only to understand the problem, not as the algorithm we will build. From an easy example, ask yourself whether there is a way to confirm that two is in the middle without creating a new array.''',50,'ex1','', 'official_1'),
sc('08-ex2','03 / OFFICIAL EXAMPLES','Example 2 — even total',[
 'nums1 = [1,2]   nums2 = [3,4]',
 'Imagine merging: [1,2,3,4]',
 'Output: 2.50000 = (2+3)/2'],
 '''In the second example, nums one holds one and two, and nums two holds three and four. In order, we get one, two, three, four. There are four elements, so there is no single element in the middle. The two central values are two and three. Add them and divide by two to get two point five. This gives us an important clue: if we split the sequence into a left half and a right half, the answer only needs the largest value on the left and the smallest value on the right.''',50,'ex2','', 'official_2'),
sc('09-examples-recap','03 / CHECK UNDERSTANDING','Two examples lead to one condition',[
 'Odd total → max(left side)',
 'Even total → [max(left)+min(right)]/2',
 'The left half must hold exactly the right number of elements.'],
 '''Let us pause and summarize. In example one, we only needed the largest value on the left. In example two, we also needed the smallest value on the right. But one thing is mandatory: the left side must contain exactly half of the elements, or one more than half when the total is odd. If the left side has the wrong count, the middle is wrong too. So our task is no longer to merge two arrays. It becomes finding a split where the count is right and the order across both sides is not broken.''',46,'recap'),
sc('10-naive','04 / FIRST HYPOTHESIS','The easiest way: merge, then find the middle',[
 'Concatenate and sort: O((m+n) log(m+n))',
 'Merge two sorted arrays: O(m+n)',
 'Correct answers, but not the required logarithmic time.'],
 '''When a problem is hard, do not skip the easiest solution. We could join the two arrays and sort them, which costs roughly the total length times the log of the total length. Because both arrays are already sorted, we could also merge them with two pointers in big O of m plus n. Both approaches give correct answers. They are very useful for checking examples and as a reference when testing. But the problem demands logarithmic time, so neither is the final solution. Telling apart correct and meeting the requirement is an important problem-solving skill.''',48,'naive'),
sc('11-reject','04 / REJECTED APPROACH','Why not just walk to the middle?',[
 'No re-sorting, but we still visit elements one by one.',
 'If the middle is thousands of positions away, linear is still linear.',
 'Use the sorted structure to skip whole groups at once.'],
 '''A seemingly better idea: do not create a new array, just use two pointers, walk to the middle position and stop. This saves memory, but the number of steps in the worst case still grows with the total size. So what are we missing? Binary search works well when each comparison lets us discard a large region of choices. If we could compare two values right next to a split and know whether to move the split left or right, we would progress much faster. That is why we need to change the question.''',47,'reject'),
sc('12-hints','05 / THREE HINTS','Think before you see the solution',[
 'Hint 1: Do we really need to build the merged array?',
 'Hint 2: Can we split both arrays so the left side has the right count?',
 'Hint 3: Which two values decide whether a split is valid?'],
 '''Before the solution, here are three hints. One: we only need one or two middle numbers, so do we really have to build the entire merged sequence? Two: imagine placing one split line on each array. Is there a way to keep the total number of elements on the left fixed? Three: because each array is sorted, is it enough to look at the two values right at the edges of the split in each array to know whether the halves are in the right order? Try drawing two split lines on paper. Do not write code. Just look for a condition you can check.''',57,'hints'),
sc('13-pause','05 / YOUR TURN','10 SECONDS TO THINK',[
 'Which condition proves that everything on the left ≤ everything on the right?',
 'No narration, no music, a countdown of exactly 10 seconds.'],
 '',10,'think',True),
sc('14-reveal','06 / DISCOVERY','Two split lines, one solution',[
 'Split each array into left / right',
 'Total elements on the left = (m+n+1)//2',
 'Find a split that respects the global order.'],
 '''Time is up. Let us see what happens when we draw a vertical line on each array. To the left of each line is a small sorted group, and the same is true on the right. If the two left groups together hold exactly the number of elements we need, and no value on the left is larger than any value on the right, then the middle is determined. The interesting part is that we do not need to compare every pair of elements. Each array is already increasing, so we only need to check the four values right beside the two split lines.''',52,'partition'),
sc('15-smaller','06 / DESIGN','Search only the shorter array',[
 'A = the shorter array; B = the longer array',
 'i = number of elements of A on the left',
 'j = leftSize − i'],
 '''We always call the shorter array A and the longer array B. If nums one starts out longer than nums two, just swap the names; the data does not change. Now, i is the number of elements of A to the left of the split. Because the total number of elements on the left is fixed, j equals leftSize minus i. So once we choose i, j is computed automatically. We only need to binary search i from zero to the length of A, including a split before the first element or after the last one.''',50,'partition'),
sc('16-four','06 / THE CONDITION','Four numbers beside the two split lines',[
 'AL = A[i−1] ; AR = A[i]',
 'BL = B[j−1] ; BR = B[j]',
 'Split at an edge? Use −∞ or +∞ as appropriate.'],
 '''Let us name four values. A left, written AL, is the last element in the left half of A. A right, written AR, is the first element in the right half of A. BL and BR are the same for array B. If we split right at the start of an array, its left side is empty, so we use minus infinity as a stand-in. If we split right at the end, its right side is empty, so we use plus infinity. These special values are not real data. They are just a compact way to avoid writing many extra branches for the edges.''',52,'bounds'),
sc('17-invariant','06 / PROOF','When is a split valid?',[
 'AL ≤ BR',
 'BL ≤ AR',
 'Two cross conditions + sorted arrays ⇒ left ≤ right.'],
 '''This is the most precise condition in the problem. A split is valid when AL is less than or equal to BR, and BL is less than or equal to AR. Why only two inequalities? Because within each array, every left element is already less than or equal to every right element of that same array. We only need to check the two cross comparisons between the arrays. When both conditions hold, the largest element on the left is the max of AL and BL, and the smallest on the right is the min of AR and BR. The median is right in front of us.''',52,'valid'),
sc('18-go-left','07 / BINARY SEARCH','If AL is too large: move the split left',[
 'AL > BR ⇒ we took too many elements from A',
 'Decrease i with hi = i−1',
 'j increases automatically to keep the left count.'],
 '''Suppose AL is greater than BR. That means we put an element of A that is too large into the left half, while a smaller element of B sits in the right half. The split cannot be correct. To fix it, we must take fewer elements from A on the left: decrease i by setting hi to i minus one. Because j equals leftSize minus i, j increases automatically. We never have to guess both splits. Every update discards about half of the remaining search range.''',49,'move_left','', 'move_left'),
sc('19-go-right','07 / BINARY SEARCH','If BL is too large: move the split right',[
 'BL > AR ⇒ we took too few elements from A',
 'Increase i with lo = i+1',
 'j decreases automatically to keep the left total.'],
 '''Now flip the situation: BL is greater than AR. An element of B on the left is larger than an element of A on the right. We are taking too few elements from A into the left side. So we increase i by setting lo to i plus one, and j decreases automatically. The two update directions are perfectly symmetric. You do not need to memorize two lines of code like a mysterious formula. Just ask which side has an element in the wrong place, then move the split to put it back in the right group.''',49,'move_right','', 'move_right'),
sc('20-walk1','08 / FOLLOW THE ALGORITHM','Walk through official example 1',[
 'A = [2], B = [1,3]',
 'leftSize = 2; try i=0, then i=1',
 'Conclusion: median = 2.0'],
 '''Let us follow the algorithm on official example one. Because nums two has only one number, A is two, and B is one and three. There are three elements in total, so leftSize is two. At first i is zero and j is two; then BL equals three, which is greater than AR, which is two. We must move i to the right. In the next step i is one and j is one. AL is two, AR is plus infinity, BL is one, and BR is three. Both conditions hold. The total is odd, so we take the max of two and one, and the result is two.''',61,'trace','', 'official_1'),
sc('21-walk2','08 / FOLLOW THE ALGORITHM','Walk through official example 2',[
 'A = [1,2], B = [3,4]',
 'leftSize = 2; find a valid split',
 'Median = (max left + min right)/2 = 2.5'],
 '''For official example two, A is one and two, and B is three and four. There are four numbers, so leftSize is two. On the first try, i is one and j is one. AL is one, AR is two, BL is three, and BR is four. BL is greater than AR, so we move i to the right. Next, i is two and j is zero. AL is two, AR is plus infinity, BL is minus infinity and BR is three. The split is valid. The total is even, so the max on the left is two, the min on the right is three, and their average is two point five.''',60,'trace','', 'official_2'),
sc('22-empty','08 / EDGE CASES','What if one array is completely empty?',[
 'A = []  B = [5]',
 'i=0, j=1; AL=−∞, AR=+∞',
 'Median = 5.0'],
 '''Let us test a case the problem allows but the two official examples do not show. Array A is empty and array B contains only the number five. Searching over A gives just one choice: i equals zero. There is one number in total, so leftSize is one and j is one. AL and AR are minus and plus infinity. The split is valid immediately, and the max on the left is five. An empty array does not require a different algorithm; the four boundary values already handle it. That is the benefit of designing a general condition.''',49,'edge'),
sc('23-duplicates','08 / EDGE CASES','Do duplicates and negatives break it?',[
 'A = [2,2]  B = [2,2] → 2.0',
 'A = [−10⁶]  B = [10⁶] → 0.0',
 'Use ≤, not <, in the validity condition.'],
 '''What if both arrays contain equal values? For example, both arrays hold two, two. The split is still valid, because both conditions use less than or equal to, not strictly less than. The median is two. With the smallest negative value and the largest positive value allowed by the problem, the median of the two numbers is zero. Both cases remind us that our comparisons must allow equality, and that negative numbers must be considered. A good test looks for the spot a hypothesis is most likely to forget.''',47,'edge'),
sc('24-pseudocode','09 / BEFORE CODE','Pseudocode: the thinking becomes a procedure',[
 '1. Make the shorter array A.',
 '2. Binary search the left count i.',
 '3. j=leftSize−i; read AL, AR, BL, BR.',
 '4. Valid: compute the median; otherwise move left/right.'],
 '''Before writing Python, let us say the algorithm in words. Step one: make sure A is the shorter array. Step two: compute how many elements must be on the left, and set the search range for i from zero to the length of A. Step three: in each try, take the middle i, compute j, and read the four boundary values, using infinity when needed. Step four: if both cross conditions hold, compute the median and stop. If AL is greater than BR, move the split in A to the left; otherwise, move it to the right. This procedure must be clear before any code appears.''',51,'pseudocode'),
sc('25-python1','10 / PYTHON 3','Python: choose the shorter array and set the split',[
 'if len(a) > len(b): a, b = b, a',
 'left_size = (m+n+1)//2',
 'lo, hi = 0, m',
 'i=(lo+hi)//2; j=left_size−i'],
 '''Only now do we reach Python three. We take the two arrays and swap the variables if the first one is longer. Let m and n be the lengths of A and B. left_size is the total plus one, integer-divided by two, which handles the odd case automatically. Set lo to zero and hi to m. Inside the loop, i is the midpoint of the search range, and j is left_size minus i. We are not looping over every element; we are only changing how many elements stand to the left of the split. Every variable in the code already has a meaning from the visuals.''',52,'code1'),
sc('26-python2','10 / PYTHON 3','Python: check the boundaries and choose a direction',[
 'AL≤BR and BL≤AR → return median',
 'AL>BR → hi=i−1',
 'Otherwise → lo=i+1',
 'Empty sides are replaced by ±∞.'],
 '''Inside the loop, the four variables a_left, a_right, b_left and b_right are just the elements beside the split. When the split goes past an edge, we use the matching infinity. If a_left does not exceed b_right and b_left does not exceed a_right, we have found the right position. If the total is odd, return the max of the two left values. If it is even, return the average of the max on the left and the min on the right. If the split is not valid yet, compare a_left with b_right to decide whether to move left or right. No step copies or re-sorts the data.''',55,'code2'),
sc('27-narrated-trace','10 / PYTHON 3','Code trace: how do the variables change?',[
 'official_2: (i,j) = (1,1) → BL>AR',
 'lo: 0 → 2',
 '(i,j) = (2,0) → VALID → 2.5'],
 '''Imagine running a debugger on example two. At first lo is zero, hi is two, i is one and j is one. The cross check shows BL, which is three, is greater than AR, which is two. The move-right branch runs, and lo goes from zero to two. On the next loop, i is two and j is zero. We read AL two, AR plus infinity, BL minus infinity, and BR three. Both inequalities hold. At the even-total check, the function returns two point five. That is a real sequence of states from the code, not an imaginary animation.''',57,'code_trace','', 'official_2'),
sc('28-complexity','11 / EVALUATION','Why is the answer O(log(m+n))?',[
 'Search the shorter array: O(log(min(m,n)+1))',
 'Each step checks four values: O(1)',
 'Extra memory: O(1)',
 'No full scan, no new array.'],
 '''Now let us evaluate the efficiency. Because i only ranges from zero to the length of the shorter array, and each comparison discards about half of the choices, the number of loops grows with the log of the shorter length. Each loop reads only four values and does a fixed amount of work, so the time is big O of log of min of m and n, plus one. That is within the problem's requirement of big O of log of m plus n. Extra memory is just a few variables and four boundary values, so it is big O of one. Do not confuse the log of the number of elements with the log of the integer values.''',50,'complexity'),
sc('29-lessons','12 / TRANSFERABLE LESSONS','Thinking you can use beyond LeetCode',[
 'Find the information you truly need.',
 'Turn the problem into a condition you can check.',
 'Exploit data that already has structure.',
 'Use counterexamples to fix a hypothesis.'],
 '''Look back at the whole journey. At first we thought we had to merge two arrays, but we only needed to find the boundary between two halves. We replaced a big task with a condition that checks four numbers. We used the existing order instead of starting over. And we used empty arrays, duplicates, and even and odd totals to verify our idea. These habits apply when you search data in a system, choose a threshold to split on, or streamline a process. The greatest value of this episode is not remembering i or j.''',49,'lessons'),
sc('30-practice','13 / RELATED PRACTICE','Three problems to train this way of thinking',[
 'LeetCode #35 — Search Insert Position',
 'LeetCode #34 — Find First and Last Position of Element',
 'LeetCode #378 — Kth Smallest Element in a Sorted Matrix'],
 '''To keep practising, try three problems. Problem thirty-five, Search Insert Position, shows that binary search can find where to insert, not just whether a value exists. Problem thirty-four, Find First and Last Position of Element, trains you to find the correct boundary when there are duplicates. Problem three hundred seventy-eight, Kth Smallest Element in a Sorted Matrix, extends the idea of finding an element by rank without sorting everything. For each one, ask yourself: what condition is true, and which choices can one check eliminate?''',54,'practice'),
sc('31-outro','KIEU STUDIO / THE ART OF CODING','Do not remember the code. Remember how you found the way.',[
 'UNDERSTAND → HYPOTHESIZE → TEST → REFLECT',
 'Problems are tools; thinking is the skill you keep.'],
 '''That completes problem four. We turned a Hard problem into a series of small, checkable questions. If next time you forget the Python code, that is fine. Draw two split lines, place the four boundary numbers, prove the validity condition yourself, and write it again. That is learning to solve real problems, not memorizing answers. Thank you for learning with Kieu Studio. See you in the next practice session of The Art of Coding.''',44,'outro'),
]
