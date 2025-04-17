import urllib.parse
from bs4 import BeautifulSoup
from retrieve_webpage import get_cached_webpage

def title_to_scholar_search_url(title: str) -> str:
    base_url = "https://scholar.google.com/scholar"
    params = {
        "hl": "en",
        "as_sdt": "0,5",
        "q": title,
        "btnG": ""
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def get_abstract_from_scholar(title: str) -> str:
	url = title_to_scholar_search_url(title)
	html_content = get_cached_webpage(url)

	soup = BeautifulSoup(html_content, 'html.parser')
	abstract_divs = soup.find_all('div', class_='gsh_csp')
	abstract_text = "\n".join([div.text.strip() for div in abstract_divs])
	link_divs = soup.find_all('div', class_='gs_or_ggsm')
	assert len(link_divs) == 1
	link = link_divs[0].find('a')['href']
	assert link.startswith('https://')
	return abstract_text, link

def assert_paper_info_correct(title: str, expected_abstract: str, expected_link: str):
	abstract, link = get_abstract_from_scholar(title)
	assert abstract == expected_abstract, f"Abstract for {title} is incorrect.\nExpected: \n{expected_abstract}\nGot: \n{abstract}"
	assert link == expected_link, f"Link for {title} is incorrect.\nExpected: \n{expected_link}\nGot: \n{link}"

	print(f"Paper {title} is correct.")


papers = [
	{
		"title": "Slashing the disaggregation tax in heterogeneous data centers with FractOS",
		"abstract": """Disaggregated heterogeneous data centers promise higher efficiency, lower total costs of ownership, and more flexibility for data-center operators. However, current software stacks can levy a high tax on application performance. Applications and OSes are designed for systems where local PCIe-connected devices are centrally managed by CPUs, but this centralization introduces unnecessary messages through the shared data-center network in a disaggregated system.
We present FractOS, a distributed OS that is designed to minimize the network overheads of disaggregation in heterogeneous data centers. FractOS elevates devices to be first-class citizens, enabling direct peer-to-peer data transfers and task invocations among them, without centralized application and OS control. FractOS achieves this through: (1) new abstractions to express distributed applications across services and disaggregated devices, (2) new mechanisms that enable devices to securely interact with each other and other data-center services, (3) a distributed and isolated OS layer that implements these abstractions and mechanisms, and can run on host CPUs and SmartNICs.
Our prototype shows that FractOS accelerates real-world heterogeneous applications by 47%, while reducing their network traffic by 3×.""",
		"link": "https://www.doc.ic.ac.uk/~lvilanov/publications/files/eurosys22_fractos.pdf"
	},
	{
		"title": "Cookie Monster: Efficient On-Device Budgeting for Differentially-Private Ad-Measurement System",
		"abstract": """With the impending removal of third-party cookies from major browsers and the introduction of new privacy-preserving advertising APIs, the research community has a timely opportunity to assist industry in qualitatively improving the Web's privacy. This paper discusses our efforts, within a W3C community group, to enhance existing privacy-preserving advertising measurement APIs. We analyze designs from Google, Apple, Meta and Mozilla, and augment them with a more rigorous and efficient differential privacy (DP) budgeting component. Our approach, called Cookie Monster, enforces well-defined DP guarantees and enables advertisers to conduct more private measurement queries accurately. By framing the privacy guarantee in terms of an individual form of DP, we can make DP budgeting more efficient than in current systems that use a traditional DP definition. We incorporate Cookie Monster into Chrome and evaluate it on microbenchmarks and advertising datasets. Across workloads, Cookie Monster significantly outperforms baselines in enabling more advertising measurements under comparable DP protection.""",
		"link": "https://dl.acm.org/doi/pdf/10.1145/3694715.3695965"
	},
	{
		"title": "LoongServe: Efficiently Serving Long-Context Large Language Models with Elastic Sequence Parallelism",
		"abstract": """The context window of large language models (LLMs) is rapidly increasing, leading to a huge variance in resource usage between different requests as well as between different phases of the same request. Restricted by static parallelism strategies, existing LLM serving systems cannot efficiently utilize the underlying resources to serve variable-length requests in different phases. To address this problem, we propose a new parallelism paradigm, elastic sequence parallelism (ESP), to elastically adapt to the variance across different requests and phases. Based on ESP, we design and build LoongServe, an LLM serving system that (1) improves computation efficiency by elastically adjusting the degree of parallelism in real-time, (2) improves communication efficiency by reducing key-value cache migration overhead and overlapping partial decoding communication with computation, and (3) improves GPU memory efficiency by reducing key-value cache fragmentation across instances. Our evaluation under diverse real-world datasets shows that LoongServe improves the throughput by up to 3.85× compared to chunked prefill and 5.81× compared to prefill-decoding disaggregation.""",
		"link": "https://arxiv.org/pdf/2404.09526"
	}
]

if __name__ == "__main__":
	for paper in papers:
		assert_paper_info_correct(paper["title"], paper["abstract"], paper["link"])
