- David Roe, Frej Drejhammar, Julian Rueth, Martin Raum, Nicolas M. Thiery, R.,
import os
import urllib, urlparse
import re

from patch import MercurialPatchMixin

from sage.env import TRAC_SERVER_URI
#
# The first line should contain a short summary of your changes, the
# following lines should contain a more detailed description. Lines
# starting with '#' are ignored.
class SageDev(MercurialPatchMixin):
                self._UI.show('The developer scripts used to store some of their data in "{0}". This file has now moved to "{1}". I moved "{0}" to "{1}". This might cause trouble if this is a fresh clone of the repository in which you never used the developer scripts before. In that case you should manually delete "{1}" now.'.format(old_file, new_file))
    def create_ticket(self):
        Create a new ticket on trac.
            :meth:`checkout`, :meth:`pull`, :meth:`edit_ticket`
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".

            Created ticket #2 at https://trac.sagemath.org/2.
            <BLANKLINE>
            #  To start work on ticket #2, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=2".
        This fails if the internet connection is broken::
            sage: dev.create_ticket()
        """
        try:
            ticket = self.trac.create_ticket_interactive()
        except OperationCancelledError:
            self._UI.debug("Ticket creation aborted.")
            raise
        except TracConnectionError as e:
            self._UI.error("A network error ocurred, ticket creation aborted.")
            raise
        ticket_url = urlparse.urljoin(self.trac._config.get('server', TRAC_SERVER_URI), str(ticket))
        self._UI.show("Created ticket #{0} at {1}.".format(ticket, ticket_url))
        self._UI.info('To start work on ticket #{0}, create a new local branch'
                      ' for this ticket with "{1}".'
                      .format(ticket, self._format_command("checkout", ticket=ticket)))
        return ticket
    def checkout(self, ticket=None, branch=None, base=''):
        r"""
        Checkout another branch.
        If ``ticket`` is specified, and ``branch`` is an existing local branch,
        then ``ticket`` will be associated to it, and ``branch`` will be
        checked out into the working directory.
        Otherwise, if there is no local branch for ``ticket``, the branch
        specified on trac will be pulled to ``branch`` unless ``base`` is
        set to something other than the empty string ``''``. If the trac ticket
        does not specify a branch yet or if ``base`` is not the empty string,
        then a new one will be created from ``base`` (per default, the master
        branch).
        If ``ticket`` is not specified, then checkout the local branch
        ``branch`` into the working directory.
        INPUT:
        - ``ticket`` -- a string or an integer identifying a ticket or ``None``
          (default: ``None``)
        - ``branch`` -- a string, the name of a local branch; if ``ticket`` is
          specified, then this defaults to ticket/``ticket``.
        - ``base`` -- a string or ``None``, a branch on which to base a new
          branch if one is going to be created (default: the empty string
          ``''`` to create the new branch from the master branch), or a ticket;
          if ``base`` is set to ``None``, then the current ticket is used. If
          ``base`` is a ticket, then the corresponding dependency will be
          added. Must be ``''`` if ``ticket`` is not specified.
        .. SEEALSO::
            :meth:`pull`, :meth:`create_ticket`, :meth:`vanilla`
        TESTS:
        Set up a single user for doctesting::
            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
        Create a few branches::
            sage: dev.git.silent.branch("branch1")
            sage: dev.git.silent.branch("branch2")

        Checking out a branch::

            sage: dev.checkout(branch="branch1")
            sage: dev.git.current_branch()
            'branch1'

        Create a ticket and checkout a branch for it::

            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            1
            sage: dev.checkout(ticket=1)
            sage: dev.git.current_branch()
            'ticket/1'
        """
        if ticket is not None:
            self.checkout_ticket(ticket=ticket, branch=branch, base=base)
        elif branch is not None:
            if base != '':
                raise SageDevValueError("base must not be specified if no ticket is specified.")
            self.checkout_branch(branch=branch)
        else:
            raise SageDevValueError("at least one of ticket or branch must be specified.")

    def checkout_ticket(self, ticket, branch=None, base=''):
        Checkout the branch associated to ``ticket``.
        associated to it, and ``branch`` will be checked out into the working directory.
        specified on trac will be pulled to ``branch`` unless ``base`` is
            :meth:`pull`, :meth:`create_ticket`, :meth:`vanilla`
        Alice tries to checkout ticket #1 which does not exist yet::
            sage: alice.checkout(ticket=1)
            ValueError: "1" is not a valid ticket name or ticket does not exist on trac.
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: bob.checkout(ticket=1)
        Now alice can check it out, even though there is no branch on the
            sage: alice.checkout(ticket=1)
        If Bob commits something to the ticket, a ``checkout`` by Alice
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.checkout(ticket=1)
        If Alice had not checked that ticket out before, she would of course
            sage: alice.checkout(ticket=1) # ticket #1 refers to the non-existant branch 'ticket/1'
            Ticket #1 refers to the non-existant local branch "ticket/1". If you have not manually interacted with git, then this is a bug in sagedev. Removing the association from ticket #1 to branch "ticket/1".
        Checking out a ticket with untracked files::
            Created ticket #2 at https://trac.sagemath.org/2.
            <BLANKLINE>
            #  To start work on ticket #2, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=2".
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
        Checking out a ticket with untracked files which make a checkout
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
            This happened while executing "git -c user.email=doc@test.test -c
            user.name=alice checkout ticket/1".
        Checking out a ticket with uncommited changes::
            sage: open("tracked", "w").close()
            sage: alice.checkout(ticket=2)
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Keep/stash] d

        Now follow some single user tests to check that the parameters are interpreted correctly::

            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
            sage: dev._wrap("_dependencies_for_ticket")

        First, create some tickets::

            sage: UI.append("Summary: ticket1\ndescription")
            sage: dev.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            1
            sage: dev.checkout(ticket=1)
            sage: UI.append("Summary: ticket2\ndescription")
            sage: dev.create_ticket()
            Created ticket #2 at https://trac.sagemath.org/2.
            <BLANKLINE>
            #  To start work on ticket #2, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=2".
            2
            sage: dev.checkout(ticket=2)
            sage: dev.git.silent.commit(allow_empty=True, message="second commit")
            sage: dev.git.commit_for_branch('ticket/2') != dev.git.commit_for_branch('ticket/1')
            True

        Check that ``base`` works::

            sage: UI.append("Summary: ticket3\ndescription")
            sage: dev.create_ticket()
            Created ticket #3 at https://trac.sagemath.org/3.
            <BLANKLINE>
            #  To start work on ticket #3, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=3".
            3
            sage: dev.checkout(ticket=3, base=2)
            sage: dev.git.commit_for_branch('ticket/3') == dev.git.commit_for_branch('ticket/2')
            True
            sage: dev._dependencies_for_ticket(3)
            (2,)
            sage: UI.append("Summary: ticket4\ndescription")
            sage: dev.create_ticket()
            Created ticket #4 at https://trac.sagemath.org/4.
            <BLANKLINE>
            #  To start work on ticket #4, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=4".
            4
            sage: dev.checkout(ticket=4, base='ticket/2')
            sage: dev.git.commit_for_branch('ticket/4') == dev.git.commit_for_branch('ticket/2')
            True
            sage: dev._dependencies_for_ticket(4)
            ()

        In this example ``base`` does not exist::

            sage: UI.append("Summary: ticket5\ndescription")
            sage: dev.create_ticket()
            Created ticket #5 at https://trac.sagemath.org/5.
            <BLANKLINE>
            #  To start work on ticket #5, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=5".
            5
            sage: dev.checkout(ticket=5, base=1000)
            ValueError: "1000" is not a valid ticket name or ticket does not exist on trac.

        In this example ``base`` does not exist locally::

            sage: UI.append("Summary: ticket6\ndescription")
            sage: dev.create_ticket()
            Created ticket #6 at https://trac.sagemath.org/6.
            <BLANKLINE>
            #  To start work on ticket #6, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=6".
            6
            sage: dev.checkout(ticket=6, base=5)
            ValueError: Branch field is not set for ticket #5 on trac.

        Creating a ticket when in detached HEAD state::

            sage: dev.git.super_silent.checkout('HEAD', detach=True)
            sage: UI.append("Summary: ticket detached\ndescription")
            sage: dev.create_ticket()
            Created ticket #7 at https://trac.sagemath.org/7.
            <BLANKLINE>
            #  To start work on ticket #7, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=7".
            7
            sage: dev.checkout(ticket=7)
            sage: dev.git.current_branch()
            'ticket/7'

        Creating a ticket when in the middle of a merge::
            sage: dev.git.super_silent.checkout('-b','merge_branch')
            sage: with open('merge', 'w') as f: f.write("version 0")
            sage: dev.git.silent.add('merge')
            sage: dev.git.silent.commit('-m','some change')
            sage: dev.git.super_silent.checkout('ticket/7')
            sage: with open('merge', 'w') as f: f.write("version 1")
            sage: dev.git.silent.add('merge')
            sage: dev.git.silent.commit('-m','conflicting change')
            sage: from sage.dev.git_error import GitError
            sage: try:
            ....:     dev.git.silent.merge('merge_branch')
            ....: except GitError: pass
            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            Created ticket #8 at https://trac.sagemath.org/8.
            <BLANKLINE>
            #  To start work on ticket #8, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=8".
            8
            sage: UI.append("n")
            sage: dev.checkout(ticket=8)
            Your repository is in an unclean state. It seems you are in the middle of a
            merge of some sort. To complete this command you have to reset your repository
            to a clean state. Do you want me to reset your repository? (This will discard
            many changes which are not commited.) [yes/No] n
            Could not check out branch "ticket/8" because your working directory is not
            in a clean state.
            <BLANKLINE>
            #  To checkout "ticket/8", use "sage --dev checkout --branch=ticket/8".
            sage: dev.git.reset_to_clean_state()

        Creating a ticket with uncommitted changes::

            sage: open('tracked', 'w').close()
            sage: dev.git.silent.add('tracked')
            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            Created ticket #9 at https://trac.sagemath.org/9.
            <BLANKLINE>
            #  To start work on ticket #9, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=9".
            9

        The new branch is based on master which is not the same commit
        as the current branch ``ticket/7``, so it is not a valid
        option to ``'keep'`` changes::

            sage: UI.append("cancel")
            sage: dev.checkout(ticket=9)
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            Could not check out branch "ticket/9" because your working directory is not
            clean.

        Finally, in this case we can keep changes because the base is
        the same commit as the current branch

            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            Created ticket #10 at https://trac.sagemath.org/10.
            <BLANKLINE>
            #  To start work on ticket #10, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=10".
            10
            sage: UI.append("keep")
            sage: dev.checkout(ticket=10, base='ticket/7')
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Keep/stash] keep
        # if branch points to an existing branch make it the ticket's branch and check it out
            self._UI.debug('The branch for ticket #{0} is now "{1}".'.format(ticket, branch))
            self._UI.debug('Now checking out branch "{0}".'.format(branch))
            self.checkout_branch(branch)
        # if there is a branch for ticket locally, check it out
                self._UI.debug('Checking out branch "{0}".'.format(branch))
                self.checkout_branch(branch)
            raise SageDevValueError('currently on no ticket, "base" must not be None')
            base = self._local_branch_for_ticket(base, pull_if_not_found=True)
                    self._UI.debug('The branch field on ticket #{0} is not set. Creating a new branch "{1}" off the master branch "{2}".'.format(ticket, branch, MASTER_BRANCH))
                    # pull the branch mentioned on trac
                        self._UI.error('The branch field on ticket #{0} is set to "{1}". However, the branch "{1}" does not exist. Please set the field on trac to a field value.'.format(ticket, remote_branch))
                        self.pull(remote_branch, branch)
                        self._UI.debug('Created a new branch "{0}" based on "{1}".'.format(branch, remote_branch))
                        self._UI.error('Could not check out ticket #{0} because the remote branch "{1}" for that ticket could not be pulled.'.format(ticket, remote_branch))
                    if not self._UI.confirm('Creating a new branch for #{0} based on "{1}". The trac ticket for #{0} already refers to the branch "{2}". As you are creating a new branch for that ticket, it seems that you want to ignore the work that has already been done on "{2}" and start afresh. Is this what you want?'.format(ticket, base, remote_branch), default=False):
                        command += self._format_command("checkout", ticket=ticket)
                        self._UI.info('To work on a fresh copy of "{0}", use "{1}".'.format(remote_branch, command))
                self._UI.debug('Creating a new branch for #{0} based on "{1}".'.format(ticket, base))
                self._UI.debug('Deleting local branch "{0}".')
            self._UI.debug("Locally recording dependency on {0} for #{1}.".format(", ".join(["#"+str(dep) for dep in dependencies]), ticket))
        self._UI.debug('Checking out to newly created branch "{0}".'.format(branch))
        self.checkout_branch(branch)
    def checkout_branch(self, branch):
        Checkout to the local branch ``branch``.
        - ``branch`` -- a string, the name of a local branch
        Checking out a branch::
            sage: dev.checkout(branch="branch1")
            sage: dev.checkout(branch="branch3")
            ValueError: Branch "branch3" does not exist locally.
        Checking out branches with untracked files::
            sage: open("untracked", "w").close()
            sage: dev.checkout(branch="branch2")
        Checking out a branch with uncommitted changes::
            sage: open("tracked", "w").close()
            sage: UI.append("cancel")
            sage: dev.checkout(branch="branch1")
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            Could not check out branch "branch1" because your working directory is not
            clean.
            sage: dev.checkout(branch="branch1")
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] s
            Your changes have been moved to the git stash stack. To re-apply your changes
            later use "git stash apply".

        And retrieve the stashed changes later::

            sage: dev.checkout(branch='branch2')
            sage: dev.git.echo.stash('apply')
            # On branch branch2
            # Changes not staged for commit:
            #   (use "git add <file>..." to update what will be committed)
            #   (use "git checkout -- <file>..." to discard changes in working directory)
            #
            #   modified:   tracked
            #
            # Untracked files:
            #   (use "git add <file>..." to include in what will be committed)
            #
            #   untracked
            no changes added to commit (use "git add" and/or "git commit -a")
            sage: UI.append("discard")
            sage: dev.checkout(branch="branch1")
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] discard
        Checking out a branch when in the middle of a merge::
            sage: dev.checkout(branch='merge_branch')
            Your repository is in an unclean state. It seems you are in the middle of a
            merge of some sort. To complete this command you have to reset your repository
            to a clean state. Do you want me to reset your repository? (This will discard
            many changes which are not commited.) [yes/No] n
            Could not check out branch "merge_branch" because your working directory is not
            in a clean state.
            <BLANKLINE>
            #  To checkout "merge_branch", use "sage --dev checkout --branch=merge_branch".
        Checking out a branch when in a detached HEAD::
            sage: dev.checkout(branch='branch1')
            sage: dev.checkout(branch='branch1')
            <BLANKLINE>
                tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] discard
        Checking out a branch with untracked files that would be overwritten by
        the checkout::
            sage: dev.checkout(branch='branch2')
            This happened while executing "git -c user.email=doc@test.test -c
            user.name=doctest checkout branch2".
            error: The following untracked working tree files would be overwritten
            by checkout:
            self._UI.error('Could not check out branch "{0}" because your working directory is not in a clean state.'
                           .format(branch))
            self._UI.info('To checkout "{0}", use "{1}".'.format(branch, self._format_command("checkout",branch=branch)))
            self.clean(error_unless_clean=(current_commit != target_commit))
            self._UI.error('Could not check out branch "{0}" because your working directory is not clean.'.format(branch))
    def pull(self, ticket_or_remote_branch=None, branch=None):
        Pull ``ticket_or_remote_branch`` to ``branch``.
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            1
            sage: alice.checkout(ticket=1)
        Bob attempts to pull for the ticket but fails because there is no
            sage: bob.pull(1)
            sage: bob.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
        Bob pulls the changes for ticket 1::
            sage: bob.pull()
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
        Alice can now pull the changes by Bob without the need to merge
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
        Now, the pull fails; one would have to use :meth:`merge`::
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
        Undo the latest commit by alice, so we can pull again::
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
            raise SageDevValueError('No "ticket_or_remote_branch" specified to pull.')
        self._UI.debug('Fetching remote branch "{0}" into "{1}".'.format(remote_branch, branch))
            self.merge(remote_branch, pull=True)
                # then just nothing happened and we can abort the pull
                e.explain = 'Fetching "{0}" into "{1}" failed.'.format(remote_branch, branch)
                    e.advice = 'You can try to use "{2}" to checkout "{1}" and then use "{3}" to resolve these conflicts manually.'.format(remote_branch, branch, self._format_command("checkout",branch=branch), self._format_command("merge",remote_branch,pull=True))
            - :meth:`push` -- Push changes to the remote server.  This
              is the next step once you've committed some changes.
            - :meth:`diff` -- Show changes that will be committed.
            sage: dev.git.super_silent.checkout('-b', 'branch1')
            sage: dev._UI.extend(["added tracked", "y", "y", "y"])
            Do you want to add "tracked"? [yes/No] y
            Do you want to commit your changes to branch "branch1"? I will prompt you for a commit message if you do. [Yes/no] y
            Do you want to commit your changes to branch "branch1"? I will prompt you for a commit message if you do. [Yes/no] y
            self._UI.info('Use "{0}" to checkout a branch.'.format(self._format_command("checkout")))
            self._UI.debug('Committing pending changes to branch "{0}".'.format(branch))
                            if self._UI.confirm('Do you want to add "{0}"?'.format(file), default=False):
                if not self._UI.confirm('Do you want to commit your changes to branch "{0}"?{1}'.format(branch, " I will prompt you for a commit message if you do." if message is None else ""), default=True):
                    self._UI.info('If you want to commit to a different branch/ticket, run "{0}" first.'.format(self._format_command("checkout")))
                self._UI.debug("A commit has been created.")
                self._UI.debug("Not creating a commit.")
            - :meth:`push` -- To push changes after setting the remote
              branch
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
                self._UI.info('Checkout a branch with "{0}" or specify branch explicitly.'.format(self._format_command('checkout')))
            self._UI.warning('The remote branch "{0}" is not in your user scope. You might not have permission to push to that branch. Did you mean to set the remote branch to "u/{1}/{0}"?'.format(remote_branch, self.trac._username))
    def push(self, ticket=None, remote_branch=None, force=False):
        Push the current branch to the Sage repository.
          set to ``remote_branch`` after the current branch has been pushed there.
          branch to push to; if ``None``, then a default is chosen
        - ``force`` -- a boolean (default: ``False``), whether to push if
            - :meth:`commit` -- Save changes to the local repository.
            - :meth:`pull` -- Update a ticket with changes from the remote
              repository.
        TESTS:
        Alice tries to push to ticket 1 which does not exist yet::
            sage: alice.push(ticket=1)
            ValueError: "1" is not a valid ticket name or ticket does not exist on trac.
        Alice creates ticket 1 and pushes some changes to it::
            sage: alice.create_ticket()
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            1
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
        Now Bob can check that ticket out and push changes himself::
            sage: bob.checkout(ticket=1)
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
        Now Alice can pull these changes::
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
        After Alice pushed her changes, Bob can not set the branch field anymore::
            sage: alice.push()
            I will now push the following new commits to the remote branch "u/alice/ticket/1":
            I will now change the branch field of ticket #1 from its current value "u/bob/ticket/1" to "u/alice/ticket/1". Is this what you want? [Yes/no] y
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            Not setting the branch field for ticket #1 to "u/bob/ticket/1" because "u/bob/ticket/1" and the current value of the branch field "u/alice/ticket/1" have diverged.
            <BLANKLINE>
            #  To overwrite the branch field use "sage --dev push --force --ticket=1
            #  --remote-branch=u/bob/ticket/1".
            #  To merge in the changes introduced by "u/alice/ticket/1", use "sage --dev
            #  download --ticket=1".
            sage: bob.pull()
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            sage: bob.push(2)
            ValueError: "2" is not a valid ticket name or ticket does not exist on trac.
            Created ticket #2 at https://trac.sagemath.org/2.
            <BLANKLINE>
            #  To start work on ticket #2, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=2".
            sage: bob.checkout(ticket=2)
            sage: bob.checkout(ticket=1)
            sage: bob.push(2)
            You are trying to push the branch "ticket/1" to "u/bob/ticket/2" for ticket #2.
            However, your local branch for ticket #2 seems to be "ticket/2". Do you really
            want to proceed? [yes/No] y
            <BLANKLINE>
            #  Use "sage --dev checkout --ticket=2 --branch=ticket/1" To permanently set the
            #  branch associated to ticket #2 to "ticket/1".
            The branch "u/bob/ticket/2" does not exist on the remote server yet. Do you want
            to create the branch? [Yes/no] y
            sage: bob.push(remote_branch="u/bob/branch1")
            The branch "u/bob/branch1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/bob/ticket/1" to "u/bob/branch1". Is this what you want? [Yes/no] y
            Merging the remote branch "u/bob/ticket/2" into the local branch "ticket/1".
            sage: bob.push()
            <BLANKLINE>
            #  Not pushing your changes because the remote branch "u/bob/ticket/1" is
            #  idential to your local branch "ticket/1". Did you forget to commit your
            #  changes with "sage --dev commit"?
            I will now change the branch field of ticket #1 from its current value
            "u/bob/branch1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            Uploading your dependencies for ticket #1: "" => "#2"
            sage: bob.push()
            <BLANKLINE>
            #  Not pushing your changes because the remote branch "u/bob/ticket/1" is
            #  idential to your local branch "ticket/1". Did you forget to commit your
            #  changes with "sage --dev commit"?
            According to trac, ticket #1 depends on #2. Your local branch depends on no
            tickets. Do you want to upload your dependencies to trac? Or do you want to
            download the dependencies from trac to your local branch? Or do you want to keep
            your local dependencies and the dependencies on trac in its current state?
            [upload/download/keep] keep
            sage: bob.push()
            <BLANKLINE>
            #  Not pushing your changes because the remote branch "u/bob/ticket/1" is
            #  idential to your local branch "ticket/1". Did you forget to commit your
            #  changes with "sage --dev commit"?
            According to trac, ticket #1 depends on #2. Your local branch depends on no
            tickets. Do you want to upload your dependencies to trac? Or do you want to
            download the dependencies from trac to your local branch? Or do you want to keep
            your local dependencies and the dependencies on trac in its current state?
            [upload/download/keep] download
            sage: bob.push()
            <BLANKLINE>
            #  Not pushing your changes because the remote branch "u/bob/ticket/1" is
            #  idential to your local branch "ticket/1". Did you forget to commit your
            #  changes with "sage --dev commit"?
            self._UI.error("Cannot push while in detached HEAD state.")
            raise OperationCancelledError("cannot push while in detached HEAD state")
                if user_confirmation or self._UI.confirm('You are trying to push the branch "{0}" to "{1}" for ticket #{2}. However, your local branch for ticket #{2} seems to be "{3}". Do you really want to proceed?'.format(branch, remote_branch, ticket, self._local_branch_for_ticket(ticket)), default=False):
                    self._UI.info('Use "{2}" To permanently set the branch associated to ticket #{0} to "{1}".'
                                  .format(ticket, branch, self._format_command("checkout",ticket=ticket,branch=branch)))
                if user_confirmation or self._UI.confirm('You are trying to push the branch "{0}" to "{1}" for ticket #{2}. However, that branch is associated to ticket #{3}. Do you really want to proceed?'.format(branch, remote_branch, ticket, self._ticket_for_local_branch(branch))):
                    self._UI.info('To permanently set the branch associated to ticket #{0} to "{1}", use "{2}". To create a new branch from "{1}" for #{0}, use "{3}" and "{4}".'.format(ticket, branch, self._format_command("checkout",ticket=ticket,branch=branch), self._format_command("checkout",ticket=ticket), self._format_command("merge", branch=branch)))
        self._UI.debug('Pushing your changes in "{0}" to "{1}".'.format(branch, remote_branch))
                if not self._UI.confirm('The branch "{0}" does not exist on the remote server yet. Do you want to create the branch?'.format(remote_branch), default=True):
                    self._UI.error('Not pushing your changes because they would discard some of the commits on the remote branch "{0}".'.format(remote_branch))
                    self._UI.info('If this is really what you want, use "{0}" to push your changes.'.format(self._format_command("push",ticket=ticket,remote_branch=remote_branch,force=True)))
                self._UI.info('Not pushing your changes because the remote branch "{0}" is idential to your local branch "{1}". Did you forget to commit your changes with "{2}"?'.format(remote_branch, branch, self._format_command("commit")))
                            if not self._UI.confirm('I will now push the following new commits to the remote branch "{0}":\n{1}Is this what you want?'.format(remote_branch, commits), default=True):
            self._UI.debug('Changes in "{0}" have been pushed to "{1}".'.format(branch, remote_branch))
            self._UI.debug("Did not push any changes.")
                self._UI.debug('Not setting the branch field for ticket #{0} because it already'
                               ' points to your branch "{1}".'.format(ticket, remote_branch))
                self._UI.debug('Setting the branch field of ticket #{0} to "{1}".'.format(ticket, remote_branch))
                        self._UI.error('Not setting the branch field for ticket #{0} to "{1}" because'
                                       ' "{1}" and the current value of the branch field "{2}" have diverged.'
                                       .format(ticket, remote_branch, current_remote_branch))
                        self._UI.info(['To overwrite the branch field use "{0}".'
                                       .format(self._format_command("push", ticket=ticket,
                                                                    remote_branch=remote_branch, force=True)),
                                       'To merge in the changes introduced by "{1}", use "{0}".'
                                       .format(self._format_command("download", ticket=ticket),
                                               current_remote_branch)])
                    if not self._UI.confirm('I will now change the branch field of ticket #{0} from its current value "{1}" to "{2}". Is this what you want?'.format(ticket, current_remote_branch, remote_branch), default=True):
        if ticket and self._has_ticket_for_local_branch(branch):
            new_dependencies_ = self._dependencies_for_ticket(self._ticket_for_local_branch(branch))
                        self._UI.debug("Setting dependencies for #{0} to {1}.".format(ticket, old_dependencies))
                self._UI.debug("Not uploading your dependencies for ticket #{0} because the dependencies on trac are already up-to-date.".format(ticket))
                self._UI.show('Uploading your dependencies for ticket #{0}: "{1}" => "{2}"'.format(ticket, old_dependencies, new_dependencies))
    def reset_to_clean_state(self, error_unless_clean=True):
        - ``error_unless_clean`` -- a boolean (default: ``True``),
          whether to raise an
          :class:`user_interface_error.OperationCancelledError` if the
            sage: dev._wrap("reset_to_clean_state")
        if not self._UI.confirm("Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. {0}Do you want me to reset your repository? (This will discard many changes which are not commited.)".format("To complete this command you have to reset your repository to a clean state. " if error_unless_clean else ""), default=False):
            if not error_unless_clean:
    def clean(self, error_unless_clean=True):
        Restore the working directory to the most recent commit.
        - ``error_unless_clean`` -- a boolean (default: ``True``),
          whether to raise an
          :class:`user_interface_error.OperationCancelledError` if the
            sage: dev.clean()
            sage: dev.clean()
            sage: dev.clean()
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] discard
            sage: dev.clean()
            sage: UI.append("cancel")
            sage: dev.clean()
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            sage: dev.clean()
            <BLANKLINE>
                 tracked
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] stash
            Your changes have been moved to the git stash stack. To re-apply your changes
            later use "git stash apply".
            sage: dev.clean()
            self.reset_to_clean_state(error_unless_clean)
        files = [line[2:] for line in self.git.status(porcelain=True).splitlines()
                 if not line.startswith('?')]

        self._UI.show(
            ['The following files in your working directory contain uncommitted changes:'] +
            [''] +
            ['    ' + f for f in files ] +
            [''])
        cancel = 'cancel' if error_unless_clean else 'keep'
        sel = self._UI.select('Discard changes?',
                              options=('discard', cancel, 'stash'), default=1)
        elif sel == cancel:
            if error_unless_clean:
            self.git.super_silent.stash()
            self._UI.show('Your changes have been moved to the git stash stack. '
                          'To re-apply your changes later use "git stash apply".')
            assert False
            :meth:`create_ticket`, :meth:`comment`,
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
    def needs_review(self, ticket=None, comment=''):
        r"""
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.
            :meth:`set_positive_review`, :meth:`comment`,
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.needs_review(comment='Review my ticket!')
        self._UI.debug("Ticket #%s marked as needing review"%ticket)
    def needs_work(self, ticket=None, comment=''):
        r"""
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.
            :meth:`set_positive_review`, :meth:`comment`,
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')
            sage: bob.checkout(ticket=1)
            sage: bob.needs_work(comment='Need to add an untracked file!')
        self._UI.debug("Ticket #%s marked as needing work"%ticket)
    def needs_info(self, ticket=None, comment=''):
        r"""
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.
            :meth:`edit_ticket`, :meth:`needs_review`,
            :meth:`positive_review`, :meth:`comment`,
            :meth:`needs_work`
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')
            sage: bob.checkout(ticket=1)
            sage: bob.needs_info(comment='Why is a tracked file enough?')
        self._UI.debug("Ticket #%s marked as needing info"%ticket)
    def positive_review(self, ticket=None, comment=''):
        r"""
        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.
            :meth:`edit_ticket`, :meth:`needs_review`,
            :meth:`needs_info`, :meth:`comment`,
            :meth:`needs_work`
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')
            sage: bob.checkout(ticket=1)
            sage: bob.positive_review()
        self._UI.debug("Ticket #%s reviewed!"%ticket)
    def comment(self, ticket=None):
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            sage: dev.comment()
            :meth:`edit_ticket`, :meth:`comment`,
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            Your branch "ticket/1" has 0 commits.
        After pushing the local branch::
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Your branch "ticket/1" has 0 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 0 commits. It does not differ from "ticket/1".
            Your branch "ticket/1" has 1 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 0 commits. "ticket/1" is ahead of "u/doctest/ticket/1" by 1 commits:
        Pushing them::
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/1":
            Your branch "ticket/1" has 1 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 1 commits. It does not differ from "ticket/1".
            Your branch "ticket/1" has 0 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 1 commits. "u/doctest/ticket/1" is ahead of "ticket/1" by 1 commits:
            sage: dev.push(remote_branch="u/doctest/branch1", force=True)
            The branch "u/doctest/branch1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Your branch "ticket/1" has 2 commits.
            The trac ticket points to the branch "u/doctest/branch1" which has 3 commits. "u/doctest/branch1" is ahead of "ticket/1" by 1 commits:
            Your remote branch "u/doctest/ticket/1" has 1 commits. The branches "u/doctest/ticket/1" and "ticket/1" have diverged.
            "u/doctest/ticket/1" is ahead of "ticket/1" by 1 commits:
            "ticket/1" is ahead of "u/doctest/ticket/1" by 2 commits:
                return 'It does not differ from "{0}".'.format(b)
                return '"{0}" is ahead of "{1}" by {2} commits:\n{3}'.format(a,b,len(b_to_a), "\n".join(b_to_a))
                return '"{0}" is ahead of "{1}" by {2} commits:\n{3}'.format(b,a,len(a_to_b),"\n".join(a_to_b))
                return 'The branches "{0}" and "{1}" have diverged.\n"{0}" is ahead of "{1}" by {2} commits:\n{3}\n"{1}" is ahead of "{0}" by {4} commits:\n{5}'.format(a,b,len(b_to_a),"\n".join(b_to_a),len(a_to_b),"\n".join(a_to_b))
            local_summary = 'Your branch "{0}" has {1} commits.'.format(branch, len(master_to_branch))
                ticket_summary = 'The trac ticket points to the branch "{0}" which does not exist.'
                ticket_summary = 'The trac ticket points to the' \
                    ' branch "{0}" which has {1} commits.'.format(ticket_branch, len(master_to_ticket))
                        ticket_summary += ' The branch can not be compared to your local' \
                            ' branch "{0}" because the branches are based on different versions' \
                            ' of sage (i.e. the "master" branch).'
            remote_summary = 'Your remote branch "{0}" has {1} commits.'.format(
                remote_branch, len(master_to_remote))
                    remote_summary += ' The branch can not be compared to your local' \
                        ' branch "{0}" because the branches are based on different version' \
                        ' of sage (i.e. the "master" branch).'
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            * #1: ticket/1 summary
            * #1: ticket/1 summary
            Cannot delete "ticket/1": is the current branch.
            <BLANKLINE>
            #  Use "sage --dev vanilla" to switch to the master branch first.
            Moved your branch "ticket/1" to "trash/ticket/1".
            <BLANKLINE>
            #  Use "sage --dev checkout --ticket=1 --base=master" to work on #1 with a clean
            #  copy of the master branch.
            - :meth:`prune_closed_tickets` -- abandon tickets that have
              been closed.
            - :meth:`local_tickets` -- list local non-abandoned tickets.
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            Cannot delete "ticket/1": is the current branch.
            <BLANKLINE>
            #  Use "sage --dev vanilla" to switch to the master branch first.
            Moved your branch "ticket/1" to "trash/ticket/1".
            <BLANKLINE>
            #  Use "sage --dev checkout --ticket=1 --base=master" to work on #1 with a clean
            #  copy of the master branch.
            sage: dev.checkout(ticket=1, base=MASTER_BRANCH)
            Creating a new branch for #1 based on "master". The trac ticket for #1
            already refers to the branch "u/doctest/ticket/1". As you are creating
            a new branch for that ticket, it seems that you want to ignore the work
            that has already been done on "u/doctest/ticket/1" and start afresh. Is
            this what you want? [yes/No] y
                raise SageDevValueError("Cannot abandon #{0}: no local branch for this ticket."
                                        .format(ticket))
                self._UI.error("Cannot delete the master branch.")
                    self._UI.error('Cannot delete "{0}": is the current branch.'
                                   .format(branch))
                    self._UI.info('Use "{0}" to switch to the master branch first.'
                                  .format(self._format_command("vanilla")))
            self._UI.show('Moved your branch "{0}" to "{1}".'
                          .format(branch, new_branch))
            self._UI.info('Use "{1}" to work on #{0} with a clean copy of the master branch.'
                          .format(ticket, self._format_command("checkout", ticket=ticket, base=MASTER_BRANCH)))
            - :meth:`merge` -- merge into the current branch rather
              than creating a new one
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            self.clean()
        self._UI.debug('Creating a new branch "{0}".'.format(branch))
                self._UI.debug('Merging {2} branch "{0}" into "{1}".'
                              .format(branch_name, branch, local_remote))
                self.merge(branch, pull=local_remote=="remote")
            self._UI.debug('Deleted branch "{0}".'.format(branch))
    def merge(self, ticket_or_branch=MASTER_BRANCH, pull=None, create_dependency=None):
          ticket, if ``pull`` is ``False``), for the name of a local or
        - ``pull`` -- a boolean or ``None`` (default: ``None``); if
          ``ticket_or_branch`` identifies a ticket, whether to pull the
          ``ticket_or_branch`` is a branch name, then ``pull`` controls
            the remote server during :meth:`push` and :meth:`pull`.
            - :meth:`show_dependencies` -- see the current
              dependencies.
            - :meth:`GitInterface.merge` -- git's merge command has
              more options and can merge multiple branches at once.
            - :meth:`gather` -- creates a new branch to merge into
              rather than merging into the current branch.
        TESTS:
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            Created ticket #2 at https://trac.sagemath.org/2.
            <BLANKLINE>
            #  To start work on ticket #2, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=2".
            sage: alice.checkout(ticket=1)
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            sage: alice.checkout(ticket=2)
            sage: alice.merge("#1", pull=False)
            Merging the local branch "ticket/1" into the local branch "ticket/2".
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/2".
            Merging the local branch "ticket/1" into the local branch "ticket/2".
        A remote branch for a local branch is only merged in if ``pull`` is set::
            Merging the local branch "ticket/1" into the local branch "ticket/2".
            sage: alice.merge("ticket/1", pull=True)
            ValueError: Branch "ticket/1" does not exist on the remote system.
            sage: bob.checkout(ticket=1)
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/2".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/2".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] resolved
        We also cannot merge if the working directory has uncommited changes::

            sage: alice._UI.append("cancel")
            sage: with open("alice2","w") as f: f.write("uncommited change")
            sage: alice.merge(1)
            The following files in your working directory contain uncommitted changes:
            <BLANKLINE>
                 alice2
            <BLANKLINE>
            Discard changes? [discard/Cancel/stash] cancel
            Cannot merge because working directory is not in a clean state.
            <BLANKLINE>
            #  Use "sage --dev commit" to commit your changes.
            self.clean()
            self._UI.show(['',
                           '#  Use "{0}" to commit your changes.'
                           .format(self._format_command('commit'))])
            self._UI.error('Not on any branch. Use "{0}" to checkout a branch.'.format(self._format_command("checkout")))
            if pull == False:
                raise SageDevValueError('"pull" must not be "False" when merging dependencies.')
                raise SageDevValueError('"create_dependency" must not be set when merging dependencies.')
                self._UI.debug("Merging dependency #{0}.".format(dependency))
                self.merge(ticket_or_branch=dependency, pull=True)
            if pull is None:
                pull = True
            if pull:
        elif pull == False or (pull is None and not self._is_remote_branch_name(ticket_or_branch, exists=True)):
            pull = False
                    raise SageDevValueError('"create_dependency" must not be "True" if "ticket_or_branch" is a local branch which is not associated to a ticket.')
            pull = True
                raise SageDevValueError('"create_dependency" must not be "True" if "ticket_or_branch" is a local branch.')
        if pull:
                self._UI.error('Can not merge remote branch "{0}". It does not exist.'
                               .format(remote_branch))
            self._UI.show('Merging the remote branch "{0}" into the local branch "{1}".'
                          .format(remote_branch, current_branch))
            self._UI.show('Merging the local branch "{0}" into the local branch "{1}".'
                          .format(branch, current_branch))
                lines.append('Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge.')
                if self._UI.select("\n".join(lines), ['resolved', 'abort']) == 'resolved':
                    self._UI.debug("Created a commit from your conflict resolution.")
                self._UI.debug("Not recording dependency on #{0} because #{1} already depends on #{0}."
                              .format(ticket, current_ticket))
    def local_tickets(self, include_abandoned=False, cached=True):
        - ``cached`` -- boolean (default: ``True``), whether to try to pull the
          summaries from the ticket cache; if ``True``, then the summaries
          might not be accurate if they changed since they were last updated.
          To update the summaries, set this to ``False``.
            - :meth:`abandon_ticket` -- hide tickets from this method.
            - :meth:`remote_status` -- also show status compared to
              the trac server.
            - :meth:`current_ticket` -- get the current ticket.
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            Created ticket #2 at https://trac.sagemath.org/2.
            <BLANKLINE>
            #  To start work on ticket #2, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=2".
            sage: dev.checkout(ticket=2)
            sage: dev.local_tickets()
                try:
                    try:
                        ticket_summary = self.trac._get_attributes(ticket, cached=cached)['summary']
                    except KeyError:
                        ticket_summary = self.trac._get_attributes(ticket, cached=False)['summary']
                except TracConnectionError:
                    ticket_summary = ""
            - :meth:`checkout` -- checkout another branch, ready to
              develop on it.
            - :meth:`pull` -- pull a branch from the server and merge
              it.
            self.clean()
            self._UI.error("Cannot checkout a release while your working directory is not clean.")
                self._UI.error('"{0}" does not exist locally or on the remote server.'.format(release))
            - :meth:`commit` -- record changes into the repository.
            - :meth:`local_tickets` -- list local tickets (you may
              want to commit your changes to a branch other than the
              current one).
            Created ticket #1 at https://trac.sagemath.org/1.
            <BLANKLINE>
            #  To start work on ticket #1, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=1".
            sage: dev.checkout(ticket=1)
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Created ticket #2 at https://trac.sagemath.org/2.
            <BLANKLINE>
            #  To start work on ticket #2, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=2".
            sage: dev.checkout(ticket=2)
            sage: dev.push()
            The branch "u/doctest/ticket/2" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Created ticket #3 at https://trac.sagemath.org/3.
            <BLANKLINE>
            #  To start work on ticket #3, create a new local branch for this ticket with
            #  "sage --dev checkout --ticket=3".
            sage: dev.checkout(ticket=3)
            sage: dev.push()
            The branch "u/doctest/ticket/3" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Merging the remote branch "u/doctest/ticket/1" into the local branch "ticket/3".
            Merging the remote branch "u/doctest/ticket/2" into the local branch "ticket/3".
            sage: dev.checkout(ticket="#1")
            sage: dev.checkout(ticket="#2")
            sage: dev.push()
            I will now push the following new commits to the remote
            branch "u/doctest/ticket/2":
            sage: dev.checkout(ticket="#3")
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/3":
            Uploading your dependencies for ticket #3: "" => "#1, #2"