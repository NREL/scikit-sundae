Review Process
==============
The code review process is essential for maintaining the quality, performance, and style consistency of the project. This guide outlines the steps for submitting and reviewing pull requests (PRs), along with best practices for both contributors and reviewers.

Reviewer Assignment
-------------------
Pull requests are reviewed by maintainers from the core development team. After submitting a PR:

* **Assignment timing:** A reviewer should be assigned within 5 business days. If not, contributors are encouraged to leave a comment on the PR to prompt assignment.
* **CI pre-checks:** Reviewers will not be assigned until the PR passes all continuous integration (CI) tests. If your PR is failing a specific unit test and you need assistance, leave a comment on the PR so the core development team can help.

Pull Request Requirements
-------------------------
Contributors must ensure the following before requesting a review:

* **Pull request template:** Fill out the PR template, verifying that all criteria (e.g., style, documentation, testing) are met.
* **CI tests:** Pushes and PRs are automatically tested using CI pipelines. Ensure all tests pass before requesting a review. If certain tests are failing, but you still believe the code is ready for review, mention this in the PR comments.

Priorities and Review Criteria
------------------------------
During the review process, the following aspects are considered:

* **Bug fixes over features:** Bug fixes take precedence over new features in the review process.
* **Performance and clarity:** We balance the importance of code performance with clarity and readability. Clear, maintainable code is prioritized alongside well-performing implementations.
* **Best Practices:** Ensure that your PR follows the project's code style and conventions (as outlined in the :doc:`patterns_and_conventions` and :doc:`code_style_and_linting` pages).

Timeline and Feedback
---------------------
* **Review timeline:** Once a reviewer is assigned, contributors should expect communication at least once per week. The development team is currently small and cannot always accommodate faster responses.
* **Splitting PRs:** For large or complex PRs, reviewers may request that the changes be split into smaller, more manageable PRs.
* **Reviewer feedback:** Reviewers should provide specific, actionable feedback on the code. Even when no changes are needed, the reviewer will leave a comment confirming that the PR meets all criteria.

Addressing Feedback
-------------------
After receiving feedback:

* **Commit changes:** Continue making commits to your branch to address reviewer comments. These updates will automatically reflect in the PR.
* **Summary and re-request:** Once all feedback is addressed, comment on the PR with a brief summary of the changes, prompting the reviewer to take another look.

Final Approval
--------------
Once the review process is complete:

* **Approval:** The reviewer will approve the PR once it meets all requirements.
* **Merging:** Approved PRs are merged into the main repository.
* **Cleanup:** Developers should delete the branch once it has been merged and shift focus to the next task.
