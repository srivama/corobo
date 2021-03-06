from tempfile import mkdtemp
from unittest.mock import create_autospec

from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitLab.GitLabIssue import GitLabIssue
from git import Repo

import plugins.git_stats
from tests.labhub_test_case import LabHubTestCase


class TestGitStats(LabHubTestCase):

    def setUp(self):
        super().setUp((plugins.git_stats.GitStats, plugins.labhub.LabHub,))
        self.labhub = self.load_plugin('LabHub')
        self.git_stats = self.load_plugin('GitStats')
        self.git_stats.REPOS = {'test': self.mock_repo}

    def test_pr_list(self):
        mock_github_mr = create_autospec(GitHubMergeRequest)
        mock_gitlab_mr = create_autospec(GitLabMergeRequest)
        mock_github_issue = create_autospec(GitHubIssue)
        mock_gitlab_issue = create_autospec(GitLabIssue)
        mock_github_mr.closes_issue = mock_github_issue
        mock_gitlab_mr.closes_issue = mock_gitlab_issue
        mock_github_mr.repository = self.mock_repo
        mock_gitlab_mr.repository = self.mock_repo
        mock_github_mr.url = 'http://www.example.com/'
        mock_gitlab_mr.url = 'http://www.example.com/'
        mock_repo_obj = create_autospec(Repo)
        cmd_github = '!mergable {}'
        cmd_gitlab = '!mergable {}'
        testbot = self

        self.mock_repo.merge_requests = [mock_github_mr]

        # Non-existing repo
        testbot.assertCommand(cmd_github.format('b'),
                              'Repository doesn\'t exist.')
        testbot.assertCommand(cmd_gitlab.format('b'),
                              'Repository doesn\'t exist.')

        # PR is suitable
        mock_github_mr.labels = ['process/approved', 'difficulty/newcomer']
        mock_gitlab_mr.labels = ['process/approved', 'difficulty/newcomer']
        mock_github_mr.state = 'open'
        mock_gitlab_mr.state = 'open'
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        mock_repo_obj.head.commit.hexsha = '1'
        mock_github_mr.base.sha = '1'
        mock_gitlab_mr.base.sha = '1'
        testbot.assertCommand(cmd_github.format('test'),
                              'PRs ready to be merged:\n '
                              'http://www.example.com/')
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        testbot.assertCommand(cmd_gitlab.format('test'),
                              'PRs ready to be merged:\n '
                              'http://www.example.com/')

        # PR is not suitable (wrong labels)
        mock_github_mr.labels = ['process/wip', 'difficulty/newcomer']
        mock_gitlab_mr.labels = ['process/wip', 'difficulty/newcomer']
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        testbot.assertCommand(cmd_github.format('test'),
                              'No merge-ready PRs!')
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        testbot.assertCommand(cmd_gitlab.format('test'),
                              'No merge-ready PRs!')
        mock_github_mr.labels = ['process/approved', 'difficulty/newcomer']
        mock_gitlab_mr.labels = ['process/approved', 'difficulty/newcomer']

        # PR is not suitable (needs rebase)
        mock_repo_obj.head.commit.hexsha = '2'
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        testbot.assertCommand(cmd_github.format('test'),
                              'No merge-ready PRs!')
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        testbot.assertCommand(cmd_gitlab.format('test'),
                              'No merge-ready PRs!')
        mock_repo_obj.head.commit.hexsha = '1'

        # PR is not suitable (already closed)
        mock_github_mr.state = 'closed'
        mock_gitlab_mr.state = 'closed'
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        testbot.assertCommand(cmd_github.format('test'),
                              'No merge-ready PRs!')
        self.mock_repo.get_clone.return_value = (
            mock_repo_obj, mkdtemp('mock_repo/'))
        testbot.assertCommand(cmd_gitlab.format('test'),
                              'No merge-ready PRs!')
