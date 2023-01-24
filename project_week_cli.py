import argparse
import itertools
import os.path
import re


def extract_headers(lines):
    headers = []
    re_hashtag_headers = r"^##* .*$"

    for i, line in enumerate(lines):
        # identify headers by leading hashtags
        if re.search(re_hashtag_headers, line):
            headers.append((i, line))

    return headers


def _appendToDictValue(dict_, key, value, allowDuplicate=True):
    if key not in dict_:
        dict_[key] = []
    append = True
    if not allowDuplicate and value in dict_[key]:
        append = False
    if append:
        dict_[key].append(value)


def parseContributors(contributors):
    """Copied from https://github.com/Slicer/slicer-wiki-scripts/blob/master/slicer_wiki_extension_module_listing.py#L343-L396"""
    # XXX This has been copied from [1]
    #     [1] https://github.com/Slicer/Slicer/blob/a8a01aa29210f938eaf48bb5c991681c3c67632d/Modules/Scripted/ExtensionWizard/ExtensionWizardLib/EditExtensionMetadataDialog.py#L101
    def _parseIndividuals(individuals):
        # Split by ',' and 'and', then flatten the list using itertools
        individuals = list(
            itertools.chain.from_iterable(
                [individual.split("and") for individual in individuals.split(",")]
            )
        )
        # Strip spaces and dot from each individuals and remove empty ones
        individuals = filter(
            None, [individual.strip().strip(".") for individual in individuals]
        )
        return individuals

    def _parseOrganization(organization):
        try:
            c = organization
            c = c.strip()
            n = c.index("(")

            individuals = _parseIndividuals(c[:n].strip())
            organization = c[n + 1 : -1].strip()

        except ValueError:
            individuals = _parseIndividuals(organization)
            organization = ""

        return (organization, individuals)

    def _parseContributors(contributors):
        orgs = re.split("(?<=[)])\s*,", contributors)
        for c in orgs:
            c = c.strip()
            if not c:
                print("  no contributors")
                continue
            (organization, individuals) = _parseOrganization(c)
            for individual in individuals:
                if individual == "":
                    print("  organization {1} has no individuals".format(organization))
                    continue
                _appendToDictValue(orgToIndividuals, organization, individual)
                _appendToDictValue(individualToOrgs, individual, organization)

    orgToIndividuals = {}
    individualToOrgs = {}

    # Split by organization
    if isinstance(contributors, str):
        contributors = [contributors]
    for contributor in contributors:
        _parseContributors(contributor)

    return (orgToIndividuals, individualToOrgs)


def parse_project_page(filepath):
    """Parse a markdown project page and return title and individuals."""

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().split("\n")

    # Strip empty lines
    content = [line for line in content if line]

    # Extract headers and associated lines as a list of (line, header) tuples
    headers = extract_headers(content)

    # Extract project title
    project_title = headers[0][1]

    # Strip `# `
    project_title = project_title[2:]

    # Extract index corresponding to `Key Investigators`
    index = [
        index
        for index, (line, header) in enumerate(headers)
        if header == "## Key Investigators"
    ][0]

    # Lines corresponding to `Key Investigators`
    key_investigators = content[headers[index][0] + 1 : headers[index + 1][0]]

    # Strip `- `
    key_investigators = [key_investigator[2:] for key_investigator in key_investigators]

    (orgToIndividuals, individualToOrgs) = parseContributors(key_investigators)

    return {
        "title": project_title,
        "investigators": list(individualToOrgs.keys()),
    }


def main():

    parser = argparse.ArgumentParser(
        prog="project_week_cli",
        description="CLI for processing project week mardown-based documents.",
    )

    parser.add_argument(
        "file",
        nargs="+",
        type=str,
        help="Provide paths to mardown project pages.",
    )

    args = parser.parse_args()

    for filepath in args.file:
        directory = os.path.dirname(filepath).split("/")[-1]
        if directory == "Projects":
            # Streamline integration with command-line lookup of README files by ignoring the template one.
            continue
        try:
            metadata = parse_project_page(filepath)
        except Exception as exc:
            print(f"Failed to process {filepath}")
            raise exc
        print(
            f"1. [{metadata['title']}](Projects/{directory}/README.md) ({', '.join(metadata['investigators'])})"
        )


if __name__ == "__main__":
    main()
