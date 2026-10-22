AI Pattern Research

Exploring Unique Patterns in Binary Images

Welcome to AI Pattern Research. This project explores how many different binary images can represent the same geometric pattern under a defined set of mathematical rules.

The project uses Python to enumerate binary images, group them into branches, identify equivalent patterns, and count the members belonging to each pattern.

1. Research Question

How many unique geometric patterns exist among all binary images at a given resolution when translation, rotation, and reflection are ignored?

We also investigate the mathematical relationship between:

- The total number of binary images.
- The number of images in each branch.
- The number of unique patterns in each branch.
- The number of original images represented by each unique pattern.

These questions are explored computationally and can be investigated further through mathematical proofs.

2. What Is a Binary Image?

A binary image contains two possible pixel values:

- `0` — black pixel
- `1` — white pixel

For an image containing `n` pixels, the total number of possible binary images is:

Total images = 2ⁿ

For example, a 4 × 4 image contains 16 pixels, so the total number of possible images is:

2¹⁶ = 65,536

3. Branches

A branch contains all binary images with exactly the same number of white pixels.

We denote the white-pixel count by `p`.

The number of members in branch `p` is:

C(n, p) = n! / (p! × (n − p)!)

For a 16-pixel image, branch `p = 2` contains:

C(16, 2) = 120 members

4. Definition of a Unique Pattern

In this project, two images are considered equivalent when their white-pixel arrangements can be matched by:

- Translation — moving the complete arrangement.
- Rotation — turning the arrangement.
- Reflection — mirroring the arrangement.

The absolute position of a shape is ignored. Its geometric arrangement is used to identify its pattern.

A canonical signature is calculated for each arrangement. Equivalent arrangements receive the same signature.

Important: This is the project's chosen definition of pattern identity. Other research may use different equivalence rules.

5. The Python Program

The Selectable-Resolution Pattern Explorer provides:

- Independently selectable image width and height.
- Exhaustive analysis for resolutions containing up to 16 pixels.
- A branch slider.
- An original-member slider.
- A unique-pattern slider.
- Original binary image and matrix displays.
- Canonical pattern visualization.
- A gallery of unique patterns within the selected branch.
- Counts showing how many original members belong to each pattern.
- Basic consistency checks.

The interface is built with Python and Tkinter. No third-party Python packages are required.

6. Research Method

The program follows these steps:

1. Generate every binary image at the selected resolution.
2. Group images by their number of white pixels.
3. Calculate a canonical signature for every image.
4. Group images with matching signatures.
5. Count the unique signatures in every branch.
6. Check that all members and pattern multiplicities are accounted for.

7. Scope and Limitations

The program exhaustively enumerates images only for resolutions containing at most 16 pixels. This limit keeps the computation manageable for a beginner-friendly desktop application.

The program's results depend on its stated definition of equivalence. Computational consistency checks are useful, but they do not independently prove every possible mathematical claim about patterns.

8. Goals

The goals of this research project are to:

- Explore geometric pattern identity.
- Compare the number of members with the number of unique patterns.
- Investigate mathematical relationships among branches.
- Make experiments reproducible.
- Invite feedback, corrections, and new ideas from other researchers and hobbyists.

9. Contributions and Discussion

Suggestions, mathematical corrections, and reproducible experiments are welcome.

The purpose of this project is to explore a mathematical question carefully, share the implementation openly, and improve our understanding through verification.

Project: AI Pattern Research

Language: Python 3

Interface: Tkinter

Analysis: Exhaustive enumeration for up to 16 pixels
