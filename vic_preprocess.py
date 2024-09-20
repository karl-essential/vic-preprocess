import argparse
import pickle
import random

from pathlib import Path


def split_content(content):
    """
    Currently the content includes a "header" consisting of short lines. These are not part of the pitch so we move them out.
    """
    # First remove some boilerplate remarks that interfere with length-based splitting.
    content = content.replace('Sign up for free guest access to view investment idea with a 45 days delay.', '')
    content = content.replace('Good news, bad news, it looks to be a bit of a hedge fund hotel.', '')
    content = content.replace('I do not hold a position with the issuer such as employment, directorship, or consultancy.', '')
    content = content.replace('I and/or others I advise hold a material investment in the issuer\'s securities.', '')
    content = content.replace('I and/or others I advise do not hold a material investment in the issuer\'s securities.', '')

    lines = content.split('\n')
    for i in range(len(lines)):
        if len(lines[i].split(' ')) > 10:  # Hack
            break
    context = '\n'.join(lines[:i])

    # Now collect the actual pitch content with some filtering hacks.
    pitch_lines = []
    for line in lines[i:]:
        if (line[:7] == 'Closing' or
            line[:7] == 'Subject' or
            line[:8] == 'Rendered' or
            line[:4] == '[I=N' or
            line[:31] == 'Please pick a category for this'
        ):
            # These are ending signals, so we stop.
            break
        if ((line[:10].lower() == 'disclaimer' and line[:48] != 'Disclaimer: It is actually a fairly liquid stock') or  # One disclaimer actually includes meaningful content...
            line[:20].lower() == 'important disclaimer' or
            line[:47] == 'This is not an offer to buy or sell a security.' or
            line == 'Disclosures / Disclaimers' or
            line[:41] == 'Any forward-looking opinions, assumptions' or
            line[:17] == 'I hold a position' or
            line[:16] == 'Legal Disclaimer' or
            '- Start deploying capital and making loans' in line or
            '- Set SBA borrowing' in line or
            '- Pay dividends' in line
        ):
            # These are boilerplate lines, but there may be meaningful content after, so we keep going.
            continue
        pitch_lines.append(line)

    pitch = '\n'.join(pitch_lines)

    return context, pitch


def main(args):
    print(args)

    with open(args.data, 'rb') as f:
        examples = pickle.load(f)

    #print(examples[0].keys())  # ['content', 'facts', 'company_ticker', 'date', 'split']

    for x in examples:
        context, pitch = split_content(x['content'])
        x['content_preprocessed'] = {'context': context, 'pitch': pitch}

    with open(Path(args.data).stem + '_preprocessed.p', 'wb') as f:
        pickle.dump(examples, f)

    with open(Path(args.data).stem + '_preprocessed.txt', 'w') as f:
        random.seed(1)
        random.shuffle(examples)
        for i, x in enumerate(examples):
            f.write('-' * 100 + '\n' + f'Example {i + 1}\n' + '-' * 100 + '\n')
            #f.write('\n[ORIGINAL]\n\n' + x['content'] + '\n\n=>\n\n')
            #f.write('\n[CONTEXT]\n\n' + x['content_preprocessed']['context'] + '\n')
            f.write('\n\n[PITCH]\n\n' + x['content_preprocessed']['pitch'] + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--data', type=str, default='good_contents_split.p')
    args = parser.parse_args()

    main(args)
