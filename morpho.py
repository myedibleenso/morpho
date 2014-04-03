from collections import defaultdict
import os


class Morpho(object):

	def __init__(self, prefixes="", suffixes="", wordlist="", verbose=False):
		self.prefixes = prefixes if os.path.exists(prefixes) else "english_prefixes.txt"
		self.suffixes = suffixes if os.path.exists(suffixes) else "english_suffixes.txt"
		self.words = self.assign_wordlist(wordlist)
		
		self.suffix_dictionary = self.make_suffix_dictionary()		
		self.prefix_dictionary = self.make_prefix_dictionary()
		
		self.word_lookup = self.make_lookup()
		self.word_rev_lookup = self.make_lookup(reverse=True)

		self.verbose = verbose
	
	def yap(self, msg):
		if self.verbose:
			print msg

	def assign_wordlist(self, wl=None):
		default_wl = "words"
		if os.path.exists(wl):
			return wl 
		
		if os.path.exists(default_wl):
			return default_wl

		else:
			raise Exception("Specify a wordlist!")

	def make_prefix_dictionary(self):
		"""
		"""
		prefix_list = [l.strip().lower() for l in open(os.path.expanduser(self.prefixes),"r").readlines() if l.strip()]

		prefix_dictionary = defaultdict(set)
		for p in prefix_list: 
			prefix_dictionary[p[0]].add(p)

		return prefix_dictionary

	def make_suffix_dictionary(self):
		"""
		"""
		rev_suffix_list = [l.strip().lower()[::-1] for l in open(os.path.expanduser(self.suffixes),"r").readlines() if l.strip()]

		suffix_dictionary = defaultdict(set)
		for s in rev_suffix_list:
			suffix_dictionary[s[0]].add(s)

		return suffix_dictionary

	def make_lookup(self, reverse=False):
		"""
		"""
		words = [w.strip().lower() for w in open(self.words, 'r').readlines()]

		#shrink the search space
		cache = dict()

		word_lookup = defaultdict(set)
		
		letter = w[0]
		if reverse: 
			letter = w[-1]

		for w in words:
		    word_lookup[letter].add(w)
		
		wordlist = []
		#these are sets
		for v in word_lookup.values():
			#concatenate lists
			wordlist += list(v)
		return word_lookup

	def longest_suffix(self, w):
		"""
		recursively seeks longest suffix
		"""
		w = w.lower()
		f = w[-1]
		
		if f not in self.suffix_dictionary: return ""

		candidates = [c[::-1] for c in self.suffix_dictionary[f]]
		candidates = [c for c in candidates if w.endswith(c)]

		if not candidates: return ""
		
		suffix = max(candidates, key=lambda x: len(x))
		self.yap("longest known suffix: {0}".format(suffix))
		remaining = w[:w.rfind(suffix)]
		#add y
		if (suffix.startswith("iz") and not remaining.endswith("l")) or \
		(remaining.endswith("f")):
			remaining += "y"
		suffix = "-" + suffix
		return self.longest_suffix(remaining) + suffix if remaining else ""

#better way is to also do suffix then look for overlap; if none, then no morpheme (ex. table)
#longest suffix is then longest_prefix - longest_suffix (prefix[prefix.rfind(suffix):])

	def longest_prefix(self, w):
		"""
		recursively seeks longest prefix
		"""
		w = w.lower()
		f = w[0]
		
		if f not in self.prefix_dictionary: return ""

		candidates = [c for c in self.prefix_dictionary[f]]
		candidates = [c for c in candidates if w.startswith(c)]

		if not candidates: return ""
		
		prefix = max(candidates, key=lambda x: len(x))
		
		self.yap("longest known prefix: {0}".format(prefix))
		remaining = w[len(prefix):]
		self.yap("remaining: {0}".format(remaining))
		prefix = prefix + "-"

		return prefix + self.longest_prefix(remaining) if remaining else ""

	def suffix_backoff(self, w):
		"""
		"""
		f = w[0]
		candidates = [c for c in self.word_lookup[f] if c in w]
		word_substring = max(candidates) if candidates else w
		return w.split(word_substring)[-1]

	def prefix_backoff(self, w):
		"""
		need a different word look up (keys should be final characters)
		"""
		l = w[-1]
		candidates = [c for c in self.word_rev_lookup[l] if c in w]
		word_substring = max(candidates) if candidates else w
		return w.split(word_substring)[0]

	def get_suffix(self, w):
		"""
		"""
		longest = self.longest_suffix(w)
		return longest if longest else self.suffix_backoff(w)

	def get_prefix(self, w):
		"""
		"""
		longest = self.longest_prefix(w)
		return longest if longest else self.prefix_backoff(w)

	def core_morpheme(self, w):
		"""
		"""
		pre = self.get_prefix(w)
		pre = pre.replace("-","")
		suf = self.get_suffix(w)
		suf = suf.replace("-","")
		return (w.split(pre)[-1]).split(suf)[0]

	def greatest_substring(self, w1, w2):
		"""
		"""
		substrings = set()
		
		for i in range(len(w1)):
			#constrain range
			for j in range(i, len(w1)):
				substring = w1[i:j+1]
				#print "substring: {0}".format(substring)
				if substring in w2:
					substrings.add(substring)

		return max(substrings)

	def smart_prefix(self, w):
		pre = self.longest_prefix(w)
		if not pre:
			return ""
		self.yap("longest prefix: {0}".format(pre))
		suf = self.get_suffix(w)
		self.yap("longest suffix: {0}".format(suf))
		shared = self.greatest_substring(pre, suf)
		self.yap("longest substring: {0}".format(shared))
		return pre.split(shared)[0]

	def smart_suffix(self, w):
		pre = self.longest_prefix(w)
		if not pre:
			return ""
		self.yap("longest prefix: {0}".format(pre))
		suf = self.get_suffix(w)
		self.yap("longest suffix: {0}".format(suf))
		shared = self.greatest_substring(pre, suf)
		self.yap("longest substring: {0}".format(shared))
		return suf.split(shared)[-1]

def demo():
	print "\n{0}\n| Demo for morpho |\n{0}".format("-"*19)
	m = Morpho()
	veg = "antivegetarianistic"
	print " core morpheme for {0}:\t{1}".format(veg, m.core_morpheme(veg))
	print "\tprefix for {0}:\t{1}".format(veg, m.get_prefix(veg))
	print "\tsuffix for {0}:\t{1}".format(veg, m.get_suffix(veg))
	print
	
if __name__ == "__main__":
	demo()
