"""English edition of Episode 02 — same scene ids, modes and timings as episode.py."""
from episode import sc

S = [
sc("01-hook","KIEU STUDIO / OUR MISSION","LeetCode is practice. Thinking is the goal.",[
    "KIEU STUDIO · THE ART OF CODING",
    "Not just finding the answer to one LeetCode problem.",
    "Every problem trains your problem-solving skills.",
    "UNDERSTAND → HYPOTHESIZE → TEST → REFLECT"],
    "Welcome to Kieu Studio, The Art of Coding. LeetCode is not the destination. It is where we practise problem solving: understanding the requirement, trying a hypothesis, testing it, and learning from the result.",19,"mission"),
sc("02-question","01 / READ THE PROBLEM","Regular Expression Matching",[
    "Input: a string s and a pattern p",
    "A dot . matches exactly one character",
    "A star * repeats the element right before it: zero or more times",
    "The match must cover the ENTIRE string"],
    "In problem ten, we must check whether a pattern matches the entire string. A dot means any single character; a star means the element before it can repeat zero or more times.",16,"problem"),
sc("03-read-input","01 / READ THE PROBLEM","Input, output and constraints",[
    "INPUT: s = the text, p = the pattern",
    "OUTPUT: true if it matches entirely; otherwise false",
    "s and p are 1 to 20 characters long",
    "s contains only a–z; p contains a–z, . and *",
    "Every * follows a valid element"],
    "The input is s and p. The output is true or false. Each string is one to twenty characters long. The pattern may only use lowercase letters, dots and stars, and every star follows a valid element.",17,"constraints"),
sc("04-stats","01 / READ THE PROBLEM","What makes this a Hard problem?",[
    "Hard · 32.0% acceptance rate",
    "About 1.52 million accepted submissions",
    "About 4.8 million total submissions",
    "Counts are submissions, not people"],
    "When we checked on the twenty-eighth of October twenty twenty-six, LeetCode rated this problem Hard, with an acceptance rate of about thirty-two percent. Remember that submissions are not the same as people.",14,"stats"),
sc("05-ex1","02 / READ THE EXAMPLES","Example 1: aa and a",[
    's = "aa"', 'p = "a"', "Output: false"],
    "The pattern has only one a, but the string has two. Even though the first character matches, one character is left unmatched, so the answer is false.",13,"ex1"),
sc("06-ex1-lesson","02 / READ THE EXAMPLES","Lesson 1: Do not miss a requirement",[
    "A partial match is not a full match",
    "Always check the finishing condition"],
    "This is the first habit: do not conclude just because one part looks right. Check the completion condition of the whole problem.",12,"lesson1"),
sc("07-ex2","02 / READ THE EXAMPLES","Example 2: aa and a*",[
    's = "aa"', 'p = "a*"', "Output: true"],
    "The star lets us use the letter a zero times, once, or many times. Using it twice is exactly how the pattern matches the whole string.",13,"ex2"),
sc("08-ex2-lesson","02 / READ THE EXAMPLES","Lesson 2: One rule, many choices",[
    'a* can be "", "a", "aa" or "aaa"...',
    "List the possibilities before you choose"],
    "The star is not just another character. It creates many choices. Recognizing every choice can be the key to the problem.",13,"lesson2"),
sc("09-ex3","02 / READ THE EXAMPLES","Example 3: ab and .*",[
    's = "ab"', 'p = ".*"', "Output: true"],
    "The dot can stand for a or for b. The star lets us repeat that rule. We use it twice to match both a and b, so the answer is true.",13,"ex3"),
sc("10-ex3-lesson","02 / READ THE EXAMPLES","Lesson 3: Combine simple rules",[
    ". is any single character",
    "* is the number of repetitions",
    ".* can match any string, including the empty one"],
    "When a problem has several rules, understand each rule first, then watch what happens when they combine.",14,"lesson3"),
sc("11-recap","02 / READ THE EXAMPLES","Three examples, three lessons",[
    "Check the ENTIRE requirement",
    "Find the points that create many choices",
    "Understand how rules interact"],
    "We have not written any code yet, but we have learned three important habits: check everything, recognize the choices, and analyse how rules combine.",12,"recap"),
sc("12-hints","03 / YOUR TURN","Three hints before the solution",[
    "HINT 1: Can you solve a smaller part?",
    "HINT 2: When you meet x*, how many choices are there?",
    "HINT 3: Do you meet the same question again?"],
    "Try thinking on your own. Can we solve the rest of the string? When we meet x star, can we skip it or use one more? And are there small questions we keep meeting again and again?",15,"hints"),
sc("13-pause","03 / YOUR TURN","10 SECONDS — YOUR TURN",[
    "If the pattern has a*, which choice do you try first?",
    "Form your own hypothesis."],
    "",10,"think",True),
sc("14-reveal","04 / BUILD THE IDEA","Break it into small questions",[
    "i = position in s",
    "j = position in p",
    "From (i, j), can the rest still match?"],
    "We replace one big question with a small one: at position i in s and position j in p, can the two remaining parts match? This is how we break a problem down.",15,"state"),
sc("15-normal","04 / BUILD THE IDEA","The ordinary case",[
    "Same letter: both move forward one step",
    "A dot: accept exactly one character, then move",
    "No match: this branch fails"],
    "For an ordinary letter or a dot, if the current character matches, we move both positions forward. If not, this path fails.",14,"normal"),
sc("16-star","04 / BUILD THE IDEA","Meeting a*: two paths",[
    "A: Skip a* entirely",
    "B: If it matches, use one character and keep a*"],
    "We have two choices. Skip a star, because it may appear zero times; or, if the current character matches a, use that character and keep a star to continue.",18,"branch"),
sc("17-tree","04 / BUILD THE IDEA","Try a path and backtrack",[
    's = "aab"; p = "c*a*b"',
    "Skip c*; use a* twice; finally match b"],
    "In the extra example a a b with c star a star b, we skip c star, use a star twice, then match b. That is a successful path.",16,"tree"),
sc("18-pitfall","04 / BUILD THE IDEA","Do not always repeat as much as possible",[
    "A greedy choice can lose the solution",
    "Keep both choices: skip and use one more"],
    "If we always use the star as much as possible, sometimes the rest no longer matches. So we must consider both choices instead of guessing.",13,"pitfall"),
sc("19-cache","05 / REMEMBER","Old questions come back",[
    "(i, j) defines one question",
    "Two branches can reach the same question",
    "Store the result and reuse it"],
    "Two different branches sometimes lead to the same pair of positions i and j. Do not solve it again. Store the answer to each small question for later. This is remembering results, also called memoization.",16,"cache"),
sc("20-dp","05 / REMEMBER","The memo table is a map of questions",[
    "Each cell asks about the remaining parts",
    "TRUE or FALSE",
    "At most about (m+1) × (n+1) states"],
    "Picture a table of positions in both strings. Each cell is a question: do the two remaining parts match? Once a cell has an answer, we never compute it again. This is dynamic programming thinking.",17,"grid"),
sc("21-dp-demo","05 / REMEMBER","A small table for aa and a*",[
    "Only pattern start j=0 and pattern end j=2",
    "A lone * is not a valid pattern on its own",
    "Use a twice, then both strings end"],
    "For a a and a star, we use a star twice and then skip it. When both remaining parts end together, the answer is true. Do not treat a lone star as a valid pattern state.",16,"dp_demo"),
sc("22-solution","06 / DESIGN THE SOLUTION","From thinking to pseudocode",[
    "match(i,j): can the remaining parts match?",
    "If the pattern ends, the string must end too",
    "With *: skip it or use one more",
    "Without *: compare characters, then move",
    "Remember the results"],
    "Before writing Python, describe the logic in words: check the end condition, take two branches when there is a star, compare characters when there is none, and remember the results.",17,"pseudocode"),
sc("23-python1","06 / PYTHON 3","Python: the function and its stopping rule",[
    "from functools import cache", "@cache", "def dfs(i, j):", "    if j == len(p):", "        return i == len(s)"],
    "The dfs function takes a pair of positions, i and j. Cache makes sure we never process the same state twice. If the pattern has ended, we succeed only if the string has ended too.",14,"code1"),
sc("24-python2","06 / PYTHON 3","Python: the two branches of a star",[
    "first = i < len(s) and (s[i] == p[j] or p[j] == '.')",
    "if j+1 < len(p) and p[j+1] == '*':",
    "    return dfs(i,j+2) or (first and dfs(i+1,j))",
    "return first and dfs(i+1,j+1)"],
    "If the next character is a star, we either skip the character and its star, or use the current character and try again. Otherwise, we only move forward when the current character matches.",18,"code2"),
sc("25-complexity","07 / EVALUATION","Why is this fast enough?",[
    "m is the length of s; n is the length of p",
    "Each state (i,j) is processed only once",
    "Time O(m × n)",
    "Memory O(m × n)"],
    "There are at most about m times n states, and each state is solved only once, so both time and memory are big O of m times n.",14,"complexity"),
sc("26-lesson","08 / PROBLEM SOLVING","Four habits to take to work",[
    "Understand the requirement exactly",
    "Test examples and counterexamples",
    "Break it into small choices",
    "Remember what you have found"],
    "What matters is not memorizing code. Remember how to understand the requirement, try a hypothesis, break choices down, and never solve the same problem twice.",15,"lessons"),
sc("27-practice","09 / PRACTICE","Three similar problems",[
    "LeetCode #44 · Wildcard Matching",
    "LeetCode #72 · Edit Distance",
    "LeetCode #97 · Interleaving String"],
    "Try Wildcard Matching, Edit Distance and Interleaving String. Do not look for code right away. First ask yourself what the small state is and what choices you have.",15,"practice"),
sc("28-outro","THE ART OF CODING","Do not memorize code. Remember how to think.",[
    "Understand → Explore → Decide → Remember",
    "KIEU STUDIO"],
    "A hard problem becomes approachable once we ask the right question. See you in the next episode of Kieu Studio, The Art of Coding.",10,"outro"),
]
