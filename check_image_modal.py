#!/usr/bin/env python3
import os

html_path = os.path.join(os.path.dirname(__file__), 'mobile', 'issue-detail.html')

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find renderIssue function
start = content.find('function renderIssue')
if start > 0:
    end = content.find('function getStatusText', start)
    render_issue = content[start:end]
    
    print('=== Checking Image Modal Code ===\n')
    print('Has onclick showImage:', 'onclick="showImage' in render_issue)
    print('Has gallery-item:', 'gallery-item' in render_issue)
    
    # Find product_image rendering
    if 'product_image' in render_issue:
        idx = render_issue.find('product_image')
        print('\n=== Product Image Code ===')
        print(render_issue[idx:idx+600])
    
    # Find issue_images rendering
    if 'issue_images' in render_issue:
        idx = render_issue.find('issue_images')
        print('\n=== Issue Images Code ===')
        print(render_issue[idx:idx+600])
else:
    print('renderIssue function not found')

# Check showImage function
show_img_start = content.find('function showImage')
if show_img_start > 0:
    show_img_end = content.find('function closeImage', show_img_start)
    print('\n=== showImage Function ===')
    print(content[show_img_start:show_img_end])

# Check closeImage function
close_img_start = content.find('function closeImage')
if close_img_start > 0:
    close_img_end = content.find('function ', close_img_start + 1)
    print('\n=== closeImage Function ===')
    print(content[close_img_start:close_img_end])
