module ufcg/softwareengineering/Ghcli

sig GithubUser{
  followers: set GithubUser,
  repos: set Repository,
  comments: set Comment,
  prs: set PullRequest
}

sig Repository{
  issues: set Issue,
  pullRequests: set PullRequest
}

sig RepositoryAsset{
  repoComments: set Comment
}

sig PullRequest extends RepositoryAsset{}

sig Issue extends RepositoryAsset{}

pred follow[from, from': GithubUser, to: GithubUser]{
  from'.followers = from.followers + to
}

pred unfollow[from, from': GithubUser, to: GithubUser]{
  from'.followers = from.followers - to
}

pred comment[from, from': GithubUser, repo, repo': RepositoryAsset, c: Comment]{
  from'.comments = from.comments
  repo'.repoComments = repo.repoComments + c
}

sig Comment{}

fact issuesMustBelongToArepository{
  all i: Issue | #i.~issues = 1
}

fact allIssuesAndPrsAreAssets{Issue + PullRequest = RepositoryAsset}

fact prsMustBelongToRepo{
  all p: PullRequest | #p.~pullRequests = 1
}

fact prsMustBelongToUser{
  all p: PullRequest | #p.~prs = 1
}

fact commentsBelongToOneIssueAndUser{
  all c: Comment | #c.~repoComments = 1 and #c.~comments = 1
}

fact commentsBelongToOnePRAndUser{
  all c: Comment | #c.~repoComments = 1 and #c.~comments = 1
}

fact allReposBelongToAnUser{
  all r: Repository | r in GithubUser.*repos
}

fact reposHaveOneOwner{
  all r: Repository | #r.~repos = 1
}

fact doesntFollowYourself{
  no u: GithubUser, f: u.followers | f = u
}

pred show(){}
run show for 8
